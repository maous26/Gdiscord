import os
import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime
import logging

# Configuration pour Render
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GUILD_ID = int(os.environ.get('GUILD_ID', '1381740173234274364'))
PORT = int(os.environ.get('PORT', 10000))

if not BOT_TOKEN:
    print("❌ BOT_TOKEN non configuré dans les variables d'environnement!")
    print("🔧 Configurez la variable d'environnement:")
    print("   BOT_TOKEN = votre_token_discord_ici")
    exit(1)

# Configuration bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration XP et rôles
XP_ROLES = [
    (0, '🌱 Nouveau'),
    (100, 'Contributeur'), 
    (500, 'Expert'),
    (1000, 'Master'),
    (2500, 'Légende'),
    (5000, 'Mythique')
]

SPECIAL_ROLES = {
    'beta_tester': '🧪 Beta Testeur',
    'bug_hunter': '🐛 Bug Hunter',
    'idea_machine': '💡 Idea Machine',
    'feedback_hero': '📊 Feedback Hero'
}

# Base de données simple
def load_db():
    try:
        with open('gearted_db.json', 'r') as f:
            return json.load(f)
    except:
        return {'users': {}}

def save_db(db):
    with open('gearted_db.json', 'w') as f:
        json.dump(db, f, indent=2)

def get_user_data(user_id):
    db = load_db()
    user_id = str(user_id)
    if user_id not in db['users']:
        db['users'][user_id] = {
            'total_xp': 0,
            'contributions': {'bugs': 0, 'features': 0, 'feedback': 0, 'beta': 0},
            'history': []
        }
        save_db(db)
    return db['users'][user_id]

def get_user_rank(user_id):
    db = load_db()
    users_xp = [(uid, data['total_xp']) for uid, data in db['users'].items()]
    users_xp.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (uid, xp) in enumerate(users_xp, 1):
        if uid == str(user_id):
            return f"#{rank}"
    return "#?"

async def safe_send(ctx, content=None, embed=None):
    """Envoi sécurisé des messages"""
    try:
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(content)
    except discord.Forbidden:
        try:
            if embed:
                await ctx.author.send(embed=embed)
            else:
                await ctx.author.send(content)
            await ctx.send(f"📬 {ctx.author.mention} J'ai envoyé ta réponse en DM")
        except:
            fallback_channel = discord.utils.get(ctx.guild.channels, name='gearted-rewards')
            if fallback_channel:
                msg = f"📢 **Réponse pour {ctx.author.mention}:**\n"
                if embed:
                    await fallback_channel.send(msg, embed=embed)
                else:
                    await fallback_channel.send(f"{msg}{content}")

@bot.event
async def on_ready():
    print(f'✅ Bot connecté: {bot.user}')
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'🏠 Serveur: {guild.name}')
        print(f'👥 Membres: {guild.member_count}')
        print('🎮 Bot Gearted prêt sur Replit!')
    else:
        print('❌ Serveur non trouvé')

@bot.command(name='gstats', aliases=['gearted_stats', 'my_gearted_stats'])
async def gearted_stats(ctx, member: discord.Member = None):
    """Voir ses stats Gearted ou celles d'un membre"""
    if not member:
        member = ctx.author
    
    user_data = get_user_data(member.id)
    
    embed = discord.Embed(
        title=f"📊 Stats de {member.display_name}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Total XP", value=f"**{user_data['total_xp']}** XP", inline=True)
    embed.add_field(name="Rang", value=get_user_rank(member.id), inline=True)
    
    # Contributions
    contrib_text = ""
    for key, value in user_data['contributions'].items():
        if value > 0:
            contrib_text += f"• {key.title()}: **{value}**\n"
    
    if contrib_text:
        embed.add_field(name="Contributions", value=contrib_text, inline=False)
    
    # Rôles et badges
    reward_roles = []
    other_roles = []
    
    # Rôles XP
    for xp_threshold, role_name in reversed(XP_ROLES):
        role = discord.utils.get(member.guild.roles, name=role_name)
        if role and role in member.roles:
            reward_roles.append(f"🏆 {role_name}")
            break
    
    # Rôles spéciaux
    for role in member.roles:
        if role.name in SPECIAL_ROLES.values():
            reward_roles.append(f"🎖️ {role.name}")
    
    # Autres rôles
    excluded_roles = ['@everyone'] + [name for _, name in XP_ROLES] + list(SPECIAL_ROLES.values())
    for role in member.roles:
        if role.name not in excluded_roles and not role.managed:
            other_roles.append(f"📋 {role.name}")
    
    all_roles = reward_roles + other_roles
    if all_roles:
        embed.add_field(name="🎭 Rôles & Badges", value="\n".join(all_roles), inline=False)
    else:
        embed.add_field(name="🎭 Rôles & Badges", value="Aucun rôle de récompense", inline=False)
    
    await safe_send(ctx, embed=embed)

@bot.command(aliases=['gleaderboard', 'gboard'])
async def leaderboard(ctx, page: int = 1):
    """Classement XP du serveur"""
    db = load_db()
    
    # Récupérer et trier les utilisateurs par XP
    users_xp = []
    for user_id, data in db['users'].items():
        try:
            member = ctx.guild.get_member(int(user_id))
            if member:
                users_xp.append((member, data['total_xp']))
        except:
            continue
    
    users_xp.sort(key=lambda x: x[1], reverse=True)
    
    # Pagination
    per_page = 10
    total_pages = (len(users_xp) + per_page - 1) // per_page
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_users = users_xp[start_idx:end_idx]
    
    embed = discord.Embed(
        title="🏆 Classement XP Gearted",
        description=f"Page {page}/{total_pages}",
        color=discord.Color.gold()
    )
    
    leaderboard_text = ""
    for i, (member, xp) in enumerate(page_users):
        rank = start_idx + i + 1
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
        leaderboard_text += f"{medal} **{member.display_name}** - {xp} XP\n"
    
    if leaderboard_text:
        embed.add_field(name="Classement", value=leaderboard_text, inline=False)
    else:
        embed.add_field(name="Aucun utilisateur", value="Pas de données XP disponibles", inline=False)
    
    await safe_send(ctx, embed=embed)

@bot.command()
async def mylinks(ctx):
    """Obtenir ses liens personnalisés pour les formulaires"""
    user_id = ctx.author.id
    username = ctx.author.display_name
    
    embed = discord.Embed(
        title="🔗 Tes Liens Personnalisés Gearted",
        description="Utilise ces liens pour que tes contributions soient reconnues automatiquement !",
        color=discord.Color.blue()
    )
    
    links = [
        ("🧪 Candidature Beta", f"https://gearted-forms.replit.app/beta-application?id={user_id}&username={username}"),
        ("🐛 Signaler un Bug", f"https://gearted-forms.replit.app/bug-report?id={user_id}&username={username}"),
        ("💡 Suggérer une Feature", f"https://gearted-forms.replit.app/feature-request?id={user_id}&username={username}"),
        ("📊 Donner un Feedback", f"https://gearted-forms.replit.app/feedback?id={user_id}&username={username}")
    ]
    
    for name, url in links:
        embed.add_field(name=name, value=f"[Accéder au formulaire]({url})", inline=False)
    
    await safe_send(ctx, embed=embed)

@bot.command()
async def update_my_roles(ctx):
    """Forcer la mise à jour de ses rôles selon XP"""
    user_data = get_user_data(ctx.author.id)
    
    # Déterminer le rôle XP approprié
    target_role = None
    for xp_threshold, role_name in reversed(XP_ROLES):
        if user_data['total_xp'] >= xp_threshold:
            target_role = discord.utils.get(ctx.guild.roles, name=role_name)
            break
    
    updated_roles = []
    
    # Ajouter le rôle XP
    if target_role and target_role not in ctx.author.roles:
        try:
            await ctx.author.add_roles(target_role)
            updated_roles.append(f"✅ Ajouté: {target_role.name}")
        except Exception as e:
            updated_roles.append(f"❌ Erreur: {e}")
    
    # Vérifier les rôles spéciaux
    contributions = user_data['contributions']
    
    special_checks = [
        ('bugs', 5, SPECIAL_ROLES['bug_hunter']),
        ('beta', 1, SPECIAL_ROLES['beta_tester']),
        ('features', 10, SPECIAL_ROLES['idea_machine']),
        ('feedback', 5, SPECIAL_ROLES['feedback_hero'])
    ]
    
    for contrib_type, threshold, role_name in special_checks:
        if contributions.get(contrib_type, 0) >= threshold:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role and role not in ctx.author.roles:
                try:
                    await ctx.author.add_roles(role)
                    updated_roles.append(f"✅ Ajouté: {role.name}")
                except Exception as e:
                    updated_roles.append(f"❌ Erreur: {e}")
    
    embed = discord.Embed(
        title="✅ Rôles Mis à Jour",
        description=f"Vérification terminée pour tes **{user_data['total_xp']} XP**!",
        color=discord.Color.green()
    )
    
    if updated_roles:
        embed.add_field(name="Modifications", value="\n".join(updated_roles), inline=False)
    else:
        embed.add_field(name="Résultat", value="Tes rôles sont déjà à jour !", inline=False)
    
    await safe_send(ctx, embed=embed)

@bot.command()
async def ping(ctx):
    """Test de connexion du bot"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"**Latence:** {latency}ms\n**Statut:** Bot opérationnel ✅\n**Hébergement:** Replit 24/7",
        color=discord.Color.green()
    )
    
    await safe_send(ctx, embed=embed)

@bot.command()
async def help_gearted(ctx):
    """Guide des commandes Gearted"""
    embed = discord.Embed(
        title="🎮 Commandes Bot Gearted",
        description="Toutes les commandes disponibles",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("📊 !gstats", "Voir tes statistiques XP et rôles"),
        ("🏆 !leaderboard", "Classement XP du serveur"),
        ("🔗 !mylinks", "Obtenir tes liens personnalisés"),
        ("🔄 !update_my_roles", "Mettre à jour tes rôles"),
        ("🏓 !ping", "Tester la connexion du bot"),
        ("❓ !help_gearted", "Afficher cette aide")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Bot hébergé 24/7 sur Replit")
    
    await safe_send(ctx, embed=embed)

@bot.command(name='update_commands_channel')
@commands.has_permissions(administrator=True)
async def update_commands_channel(ctx):
    """Commande pour mettre à jour le canal 📚┃commandes"""
    
    # Chercher le canal
    target_channel = discord.utils.get(ctx.guild.channels, name="📚┃commandes")
    if not target_channel:
        await ctx.send("❌ Canal 📚┃commandes non trouvé")
        return
    
    # Créer l'embed
    embed = discord.Embed(
        title="🎮 Bot Gearted - Guide des Commandes",
        description="**Toutes les commandes disponibles • Bot opérationnel 24/7**",
        color=0x2ecc71
    )
    
    embed.add_field(
        name="📊 **Statistiques & Classement**",
        value=(
            "🎯 **`!gstats`** - Affiche tes statistiques XP et rôles\n"
            "👤 **`!gstats @membre`** - Consulter les stats d'un autre membre\n"
            "🏆 **`!leaderboard`** - Classement XP complet du serveur"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔧 **Gestion & Personnalisation**",
        value=(
            "🔄 **`!update_my_roles`** - Force la mise à jour de tes rôles\n"
            "🔗 **`!mylinks`** - Accès à tes liens formulaires personnalisés"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ **Système & Support**",
        value=(
            "📡 **`!ping`** - Test de connexion et latence du bot\n"
            "📚 **`!help_gearted`** - Guide d'aide détaillé et support"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🏅 **Système de Rôles XP**",
        value=(
            "🌱 **Nouveau** (0+ XP)\n🚀 **Contributeur** (100+ XP)\n⭐ **Expert** (500+ XP)\n💎 **Master** (1000+ XP)\n👑 **Légende** (2500+ XP)\n🔥 **Mythique** (5000+ XP)"
        ),
        inline=True
    )
    
    embed.add_field(
        name="🎖️ **Badges Spéciaux**",
        value=(
            "🧪 **Beta Testeur**\n🐛 **Bug Hunter** (5+ bugs)\n💡 **Idea Machine** (10+ idées)\n📊 **Feedback Hero** (5+ retours)"
        ),
        inline=True
    )
    
    embed.add_field(
        name="💰 **Comment Gagner de l'XP**",
        value=(
            "🎯 Utilise **`!mylinks`** pour accéder aux formulaires\n"
            "🐛 Signale des bugs • 💡 Propose des idées\n"
            "🧪 Participe aux tests beta • 📈 Donne des feedbacks\n"
            "⚡ **XP attribués automatiquement !**"
        ),
        inline=False
    )
    
    embed.set_footer(text="✨ Bot Gearted • Communauté Airsoft • 13 juin 2025")
    
    try:
        # Nettoyer le canal
        await target_channel.purge(limit=15)
        
        # Envoyer le guide
        message = await target_channel.send(embed=embed)
        
        # Épingler
        await message.pin()
        
        await ctx.send(f"✅ Canal {target_channel.mention} mis à jour avec succès!")
        
    except discord.Forbidden:
        await ctx.send("❌ Permissions insuffisantes pour modifier le canal")
    except Exception as e:
        await ctx.send(f"❌ Erreur: {e}")

# Keep alive pour Replit
from threading import Thread
import time

def keep_alive():
    """Garde le bot actif sur Replit"""
    while True:
        time.sleep(300)  # 5 minutes

# Serveur Flask pour Render health check
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "online" if bot.is_ready() else "connecting"}

@app.route('/')
def home():
    return {"message": "Gearted Discord Bot is running!", "status": "active"}

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False)

# Lancement du bot
if __name__ == "__main__":
    print(f"🚀 Démarrage du bot Gearted sur Render (Port: {PORT})...")
    
    # Démarrer le serveur Flask en arrière-plan
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("🔧 Vérifiez la configuration des variables d'environnement")
