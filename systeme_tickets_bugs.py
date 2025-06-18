#!/usr/bin/env python3
"""
SYSTÈME TICKETS BUGS - GEARTED MARKETPLACE
==========================================
Gère automatiquement la création et le suivi des tickets pour
signaler les bugs de l'écosystème Gearted.
"""

import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta
import uuid

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GUILD_ID = int(os.environ.get('GUILD_ID', '1381740173234274364'))

if not BOT_TOKEN:
    print("❌ BOT_TOKEN non configuré dans les variables d'environnement!")
    print("🔧 Configurez la variable d'environnement BOT_TOKEN")
    exit(1)

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!bug_', intents=intents)

# Priorités des bugs
BUG_PRIORITIES = {
    'critique': {
        'emoji': '🔴',
        'color': 0xff0000,
        'response_time': 2,  # heures
        'xp_reward': 500,
        'description': 'Crash, perte de données, fonctionnalité principale cassée'
    },
    'haute': {
        'emoji': '🟠', 
        'color': 0xff8800,
        'response_time': 24,
        'xp_reward': 200,
        'description': 'Fonctionnalité importante défaillante'
    },
    'moyenne': {
        'emoji': '🟡',
        'color': 0xffff00,
        'response_time': 48,
        'xp_reward': 100,
        'description': 'Problèmes d\'affichage, fonctionnalités secondaires'
    },
    'basse': {
        'emoji': '🟢',
        'color': 0x00ff00,
        'response_time': 72,
        'xp_reward': 50,
        'description': 'Problèmes esthétiques, bugs mineurs'
    }
}

# Plateformes supportées
PLATFORMS = {
    'mobile': '📱 Application Mobile',
    'web': '🌐 Site Web',
    'discord': '🤖 Bot Discord',
    'forms': '📝 Formulaires'
}

# Statuts des tickets
TICKET_STATUS = {
    'nouveau': {'emoji': '🆕', 'name': 'Nouveau'},
    'analyse': {'emoji': '📋', 'name': 'En cours d\'analyse'},
    'dev': {'emoji': '🔍', 'name': 'En développement'},
    'test': {'emoji': '🧪', 'name': 'En test'},
    'resolu': {'emoji': '✅', 'name': 'Résolu'},
    'ferme': {'emoji': '🔒', 'name': 'Fermé'}
}

@bot.event
async def on_ready():
    print(f'🎫 Système Tickets Bugs connecté: {bot.user}')
    
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Serveur non trouvé")
        return
    
    print(f"🏠 Serveur: {guild.name}")
    
    # Configuration initiale
    await setup_ticket_system(guild)
    
    print("✅ Système de tickets bugs prêt !")

async def setup_ticket_system(guild):
    """Configure le système de tickets bugs"""
    print("\n🎫 CONFIGURATION SYSTÈME TICKETS")
    print("=" * 40)
    
    # 1. Créer la catégorie Support si nécessaire
    support_category = discord.utils.get(guild.categories, name='🆘 SUPPORT')
    
    if not support_category:
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
            }
            
            support_category = await guild.create_category(
                '🆘 SUPPORT',
                overwrites=overwrites,
                reason='Catégorie pour support et tickets'
            )
            print(f"✅ Catégorie créée: {support_category.name}")
        except Exception as e:
            print(f"❌ Erreur création catégorie: {e}")
            return
    
    # 2. Créer le salon tickets-bugs
    tickets_channel = discord.utils.get(guild.text_channels, name='🎫┃tickets-bugs')
    
    if not tickets_channel:
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    add_reactions=True,
                    read_message_history=True
                ),
                guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    manage_messages=True
                )
            }
            
            tickets_channel = await support_category.create_text_channel(
                '🎫┃tickets-bugs',
                topic='🐛 Signaler des bugs • Créez un ticket privé pour déclarer un problème',
                overwrites=overwrites
            )
            print(f"✅ Canal créé: {tickets_channel.name}")
        except Exception as e:
            print(f"❌ Erreur création canal: {e}")
            return
    
    # 3. Publier le message de création de tickets
    await post_ticket_creation_message(tickets_channel)
    
    # 4. Créer les rôles de support si nécessaire
    await setup_support_roles(guild)

async def setup_support_roles(guild):
    """Créer les rôles de support"""
    print("\n🛡️ CONFIGURATION RÔLES SUPPORT")
    print("-" * 30)
    
    support_roles = {
        '🆘 Support Team': {
            'color': discord.Color.blue(),
            'permissions': ['view_channel', 'send_messages', 'manage_messages', 'kick_members']
        },
        '🔧 Bug Tracker': {
            'color': discord.Color.orange(),
            'permissions': ['view_channel', 'send_messages', 'manage_messages']
        }
    }
    
    for role_name, config in support_roles.items():
        existing_role = discord.utils.get(guild.roles, name=role_name)
        
        if not existing_role:
            try:
                permissions = discord.Permissions.none()
                for perm in config['permissions']:
                    setattr(permissions, perm, True)
                
                role = await guild.create_role(
                    name=role_name,
                    color=config['color'],
                    permissions=permissions,
                    hoist=True,
                    mentionable=True,
                    reason='Rôle pour gestion tickets bugs'
                )
                print(f"✅ Rôle créé: {role.name}")
            except Exception as e:
                print(f"❌ Erreur création rôle {role_name}: {e}")
        else:
            print(f"✅ Rôle existant: {role_name}")

async def post_ticket_creation_message(channel):
    """Poste le message principal de création de tickets"""
    
    # Supprimer les anciens messages
    async for message in channel.history(limit=50):
        if message.author == bot.user:
            await message.delete()
    
    # Message principal
    main_embed = discord.Embed(
        title="🐛 SIGNALEMENT DE BUGS",
        description="""**Bienvenue dans le système de tickets bugs Gearted !**

Ce salon vous permet de signaler facilement tous les bugs rencontrés sur notre écosystème.

🎯 **Que signaler ici :**
📱 Application mobile Gearted
🌐 Site web marketplace  
🤖 Bot Discord
📝 Formulaires en ligne

⚡ **Comment ça marche :**
1. Cliquez sur **🐛 Signaler un Bug** ci-dessous
2. Un salon privé sera créé automatiquement
3. Suivez le guide pour décrire votre problème
4. Notre équipe vous répondra rapidement !

🏆 **Récompenses XP :**
🔴 Bug critique : **500 XP** + Badge
🟠 Bug important : **200 XP**
🟡 Bug moyen : **100 XP**
🟢 Bug mineur : **50 XP**""",
        color=0x3498db
    )
    
    main_embed.add_field(
        name="⏰ Temps de réponse garantis",
        value="🔴 Critique: < 2h\n🟠 Important: < 24h\n🟡 Moyen: < 48h\n🟢 Mineur: < 72h",
        inline=True
    )
    
    main_embed.add_field(
        name="👥 Équipe de support",
        value="🛡️ Modérateurs\n🔧 Développeurs\n⚙️ Administrateurs",
        inline=True
    )
    
    main_embed.set_footer(text="💡 Tip: Plus votre description est précise, plus vite nous pourrons résoudre le problème !")
    
    # Boutons de création
    view = TicketCreationView()
    
    await channel.send(embed=main_embed, view=view)
    
    # Message d'instructions
    instructions_embed = discord.Embed(
        title="📋 GUIDE DE SIGNALEMENT",
        description="""**Pour un signalement efficace, indiquez :**

**📱 Plateforme concernée**
Application, site web, bot Discord, formulaires...

**📋 Description claire**
Que se passe-t-il exactement ?

**🔄 Étapes pour reproduire**
Comment déclencher le bug ?

**✅ Résultat attendu**
Que devrait-il se passer normalement ?

**❌ Résultat obtenu**
Que se passe-t-il à la place ?

**📱 Informations techniques**
Appareil, navigateur, version...

**📸 Captures d'écran**
Images du problème (très utile !)""",
        color=0xf39c12
    )
    
    await channel.send(embed=instructions_embed)

class TicketCreationView(discord.ui.View):
    """Interface de création de tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='🐛 Signaler un Bug', style=discord.ButtonStyle.danger, custom_id='create_bug_ticket')
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer un nouveau ticket bug"""
        
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        guild = interaction.guild
        existing_ticket = None
        
        for channel in guild.text_channels:
            if (channel.name.startswith(f'ticket-bug-{interaction.user.name.lower()}') and 
                not channel.name.endswith('-fermé')):
                existing_ticket = channel
                break
        
        if existing_ticket:
            await interaction.response.send_message(
                f"❌ Vous avez déjà un ticket ouvert : {existing_ticket.mention}\n"
                f"Fermez-le d'abord ou utilisez-le pour signaler d'autres bugs.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Créer le ticket
        ticket_channel = await create_bug_ticket(interaction.user, guild)
        
        if ticket_channel:
            await interaction.followup.send(
                f"✅ Ticket créé avec succès !\n"
                f"Rendez-vous dans {ticket_channel.mention} pour décrire votre bug.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ Erreur lors de la création du ticket. Contactez un administrateur.",
                ephemeral=True
            )

async def create_bug_ticket(user, guild):
    """Créer un nouveau ticket bug pour un utilisateur"""
    
    # Trouver la catégorie support
    support_category = discord.utils.get(guild.categories, name='🆘 SUPPORT')
    
    if not support_category:
        return None
    
    # Générer un ID unique pour le ticket
    ticket_id = str(uuid.uuid4())[:8]
    channel_name = f'ticket-bug-{user.name.lower()}-{ticket_id}'
    
    try:
        # Permissions du canal privé
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True
            )
        }
        
        # Ajouter permissions pour l'équipe de support
        support_roles = ['🆘 Support Team', '🔧 Bug Tracker', '⚙️ Admin', '👑 Fondateur']
        for role_name in support_roles:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_messages=True
                )
        
        # Créer le canal
        ticket_channel = await support_category.create_text_channel(
            channel_name,
            topic=f'🐛 Ticket bug de {user.display_name}',
            overwrites=overwrites
        )
        
        # Message de bienvenue dans le ticket
        await post_ticket_welcome_message(ticket_channel, user)
        
        return ticket_channel
        
    except Exception as e:
        print(f"❌ Erreur création ticket: {e}")
        return None

async def post_ticket_welcome_message(channel, user):
    """Poste le message de bienvenue dans un nouveau ticket"""
    
    embed = discord.Embed(
        title=f"🐛 Ticket Bug #{channel.name.split('-')[-1]}",
        description=f"""**Bonjour {user.mention} !**

Merci d'avoir créé un ticket pour signaler un bug. Notre équipe va examiner votre problème rapidement.

**📋 Pour nous aider, veuillez remplir ce formulaire :**""",
        color=0xe74c3c
    )
    
    embed.add_field(
        name="📱 **PLATEFORME CONCERNÉE**",
        value="Cochez celle qui correspond :\n" +
              "□ Application mobile\n" +
              "□ Site web marketplace\n" +
              "□ Bot Discord\n" +
              "□ Formulaires en ligne\n" +
              "□ Autre : ___________",
        inline=False
    )
    
    embed.add_field(
        name="📋 **DESCRIPTION DU PROBLÈME**",
        value="Décrivez clairement ce qui ne fonctionne pas :",
        inline=False
    )
    
    embed.add_field(
        name="🔄 **ÉTAPES POUR REPRODUIRE**",
        value="Listez les actions qui déclenchent le bug :\n1. \n2. \n3. ",
        inline=False
    )
    
    embed.add_field(
        name="✅ **RÉSULTAT ATTENDU**",
        value="Que devrait-il se passer normalement ?",
        inline=True
    )
    
    embed.add_field(
        name="❌ **RÉSULTAT OBTENU**",
        value="Que se passe-t-il à la place ?",
        inline=True
    )
    
    embed.add_field(
        name="📱 **INFORMATIONS TECHNIQUES**",
        value="• Appareil : [iPhone, Android, PC, etc.]\n• Navigateur : [Chrome, Safari, etc.]\n• Version : [Si connue]",
        inline=False
    )
    
    embed.set_footer(text="💡 N'hésitez pas à joindre des captures d'écran !")
    
    # Boutons de gestion
    view = TicketManagementView()
    
    message = await channel.send(embed=embed, view=view)
    
    # Mentionner l'équipe de support
    support_role = discord.utils.get(channel.guild.roles, name='🆘 Support Team')
    if support_role:
        await channel.send(f"{support_role.mention} Nouveau ticket bug créé !")

class TicketManagementView(discord.ui.View):
    """Boutons de gestion des tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='🏷️ Définir Priorité', style=discord.ButtonStyle.secondary, custom_id='set_priority')
    async def set_priority(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir la priorité du ticket"""
        
        # Vérifier permissions
        if not any(role.name in ['🆘 Support Team', '🔧 Bug Tracker', '⚙️ Admin', '👑 Fondateur'] 
                  for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Seule l'équipe de support peut définir la priorité.", 
                ephemeral=True
            )
            return
        
        # Menu de sélection de priorité
        select = PrioritySelect()
        view = discord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message(
            "🏷️ Sélectionnez la priorité de ce bug :",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label='✅ Marquer Résolu', style=discord.ButtonStyle.success, custom_id='mark_resolved')
    async def mark_resolved(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Marquer le ticket comme résolu"""
        
        # Vérifier permissions
        if not any(role.name in ['🆘 Support Team', '🔧 Bug Tracker', '⚙️ Admin', '👑 Fondateur'] 
                  for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Seule l'équipe de support peut marquer un ticket comme résolu.", 
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Changer le nom du canal
        new_name = interaction.channel.name + '-résolu'
        await interaction.channel.edit(name=new_name)
        
        # Message de résolution
        embed = discord.Embed(
            title="✅ Ticket Résolu",
            description="Ce ticket a été marqué comme résolu par l'équipe de support.\n\n"
                       "Si le problème persiste, vous pouvez demander la réouverture.",
            color=0x27ae60
        )
        embed.set_footer(text=f"Résolu par {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label='🔒 Fermer Ticket', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Fermer définitivement le ticket"""
        
        # Créateur du ticket ou équipe de support
        channel_creator = interaction.channel.name.split('-')[2]
        is_creator = interaction.user.name.lower() == channel_creator
        is_support = any(role.name in ['🆘 Support Team', '🔧 Bug Tracker', '⚙️ Admin', '👑 Fondateur'] 
                        for role in interaction.user.roles)
        
        if not (is_creator or is_support):
            await interaction.response.send_message(
                "❌ Seul le créateur du ticket ou l'équipe de support peut le fermer.", 
                ephemeral=True
            )
            return
        
        # Confirmation
        confirm_view = TicketCloseConfirmView()
        
        await interaction.response.send_message(
            "⚠️ **Confirmer la fermeture ?**\n\n"
            "Cette action supprimera définitivement ce canal dans 30 secondes.\n"
            "Assurez-vous d'avoir sauvegardé toutes les informations importantes.",
            view=confirm_view,
            ephemeral=True
        )

class PrioritySelect(discord.ui.Select):
    """Menu de sélection de priorité"""
    
    def __init__(self):
        options = []
        
        for priority, config in BUG_PRIORITIES.items():
            options.append(discord.SelectOption(
                label=f"{config['emoji']} {priority.title()}",
                description=config['description'],
                value=priority
            ))
        
        super().__init__(placeholder="Choisir la priorité...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        priority = self.values[0]
        config = BUG_PRIORITIES[priority]
        
        # Mettre à jour le nom du canal
        current_name = interaction.channel.name
        new_name = f"{config['emoji']}-{current_name}"
        
        await interaction.channel.edit(name=new_name)
        
        # Message de confirmation
        embed = discord.Embed(
            title=f"{config['emoji']} Priorité Définie",
            description=f"**Priorité :** {priority.title()}\n"
                       f"**Temps de réponse cible :** {config['response_time']}h\n"
                       f"**Récompense XP :** {config['xp_reward']} XP",
            color=config['color']
        )
        
        await interaction.response.send_message(embed=embed)

class TicketCloseConfirmView(discord.ui.View):
    """Confirmation de fermeture de ticket"""
    
    def __init__(self):
        super().__init__(timeout=30)
    
    @discord.ui.button(label='✅ Confirmer', style=discord.ButtonStyle.danger)
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔒 Ticket fermé. Ce canal sera supprimé dans 10 secondes...",
            ephemeral=True
        )
        
        await asyncio.sleep(10)
        await interaction.channel.delete(reason="Ticket fermé par l'utilisateur")
    
    @discord.ui.button(label='❌ Annuler', style=discord.ButtonStyle.secondary)
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Fermeture annulée.", ephemeral=True)
        self.stop()

# Commandes administratives
@bot.command()
@commands.has_any_role("⚙️ Admin", "👑 Fondateur", "🆘 Support Team")
async def ticket_stats(ctx):
    """Statistiques des tickets bugs"""
    
    guild = ctx.guild
    
    # Compter les tickets
    active_tickets = []
    resolved_tickets = []
    
    for channel in guild.text_channels:
        if channel.name.startswith('ticket-bug-'):
            if '-résolu' in channel.name or '-fermé' in channel.name:
                resolved_tickets.append(channel)
            else:
                active_tickets.append(channel)
    
    # Compter par priorité
    priority_counts = {'critique': 0, 'haute': 0, 'moyenne': 0, 'basse': 0, 'non-définie': 0}
    
    for channel in active_tickets:
        found_priority = False
        for priority, config in BUG_PRIORITIES.items():
            if config['emoji'] in channel.name:
                priority_counts[priority] += 1
                found_priority = True
                break
        if not found_priority:
            priority_counts['non-définie'] += 1
    
    embed = discord.Embed(
        title="📊 Statistiques Tickets Bugs",
        color=0x3498db
    )
    
    embed.add_field(
        name="📈 Aperçu général",
        value=f"🆕 Tickets actifs: **{len(active_tickets)}**\n"
              f"✅ Tickets résolus: **{len(resolved_tickets)}**\n"
              f"📊 Total: **{len(active_tickets) + len(resolved_tickets)}**",
        inline=True
    )
    
    embed.add_field(
        name="🏷️ Répartition par priorité",
        value=f"🔴 Critique: **{priority_counts['critique']}**\n"
              f"🟠 Haute: **{priority_counts['haute']}**\n"
              f"🟡 Moyenne: **{priority_counts['moyenne']}**\n"
              f"🟢 Basse: **{priority_counts['basse']}**\n"
              f"⚪ Non définie: **{priority_counts['non-définie']}**",
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_any_role("⚙️ Admin", "👑 Fondateur")
async def setup_tickets(ctx):
    """Reconfigurer le système de tickets"""
    
    await setup_ticket_system(ctx.guild)
    await ctx.send("✅ Système de tickets reconfiguré !")

if __name__ == "__main__":
    print("🎫 SYSTÈME TICKETS BUGS - GEARTED")
    print("=" * 50)
    print("Ce script configure:")
    print("• Salon de création de tickets bugs")
    print("• Interface de gestion automatisée") 
    print("• Système de priorités et récompenses")
    print("• Suivi et statistiques")
    print("=" * 50)
    
    bot.run(BOT_TOKEN)
