# Gearted Discord Bot

Un bot Discord complet pour la communauté Airsoft Gearted avec système XP, modération automatisée et gestion des tickets.

## 🚀 Fonctionnalités

- **Système XP automatique** avec 6 niveaux de progression
- **Modération automatisée** avec rôles sécurisés
- **Système de tickets bugs** avec classification par priorité
- **Formulaires de candidature** intégrés
- **6 commandes essentielles** optimisées

## 🎮 Commandes Disponibles

| Commande | Description | Usage |
|----------|-------------|-------|
| `!gstats` | Statistiques XP et rôles | `!gstats` ou `!gstats @membre` |
| `!leaderboard` | Classement XP du serveur | `!leaderboard` |
| `!update_my_roles` | Met à jour vos rôles | `!update_my_roles` |
| `!mylinks` | Liens formulaires personnalisés | `!mylinks` |
| `!ping` | Test de connexion | `!ping` |
| `!help_gearted` | Guide complet | `!help_gearted` |

## 🏅 Système de Rôles XP

- 🌱 **Nouveau** (0+ XP)
- 🚀 **Contributeur** (100+ XP)
- ⭐ **Expert** (500+ XP)
- 💎 **Master** (1000+ XP)
- 👑 **Légende** (2500+ XP)
- 🔥 **Mythique** (5000+ XP)

## 🎖️ Badges Spéciaux

- 🧪 **Beta Testeur**
- 🐛 **Bug Hunter** (5+ bugs signalés)
- 💡 **Idea Machine** (10+ idées proposées)
- 📊 **Feedback Hero** (5+ retours donnés)

## 🚀 Déploiement sur Render

### Variables d'environnement requises :

```bash
BOT_TOKEN=your_discord_bot_token_here
GUILD_ID=1381740173234274364
PORT=10000
```

### Commandes de build :

```bash
pip install -r requirements.txt
```

### Commande de démarrage :

```bash
python main.py
```

## 📁 Structure du Projet

```
├── main.py                 # Bot principal optimisé
├── requirements.txt        # Dépendances Python
├── render.yaml            # Configuration Render
├── keep_alive.py          # Keep-alive pour Render
├── gearted_db.json        # Base de données XP
└── docs/                  # Documentation complète
```

## 🛡️ Système de Modération

- Rôle `🛡️ Modérateur` avec permissions sécurisées
- Canaux privés de modération automatiquement créés
- Logs automatiques des actions de modération
- Formulaire de candidature modérateur intégré

## 🎫 Système de Tickets

- Création automatique de tickets bugs
- Classification par priorité (Critical, High, Medium, Low)
- Récompenses XP automatiques selon la priorité
- Canaux privés par ticket avec workflow automatisé

## 💰 Comment Gagner de l'XP

1. Utilise `!mylinks` pour accéder aux formulaires
2. Signale des bugs via le système de tickets
3. Propose des améliorations et nouvelles idées
4. Participe aux tests beta des fonctionnalités
5. Donne des feedbacks constructifs sur le marketplace

**XP attribués automatiquement par le bot !**

## 📞 Support

Pour toute question ou problème :
- Utilise la commande `!help_gearted` dans Discord
- Crée un ticket via le système intégré
- Consulte la documentation dans le dossier `docs/`

## 🏆 Statut

**✅ PRODUCTION READY**

Le bot Gearted est 100% opérationnel et prêt pour un déploiement en production. Toutes les fonctionnalités principales sont implémentées, testées et documentées.

---

**Développé pour la communauté Airsoft Gearted • Juin 2025**
