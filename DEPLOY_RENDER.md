# 🚀 Guide de Déploiement Render - Bot Discord Gearted

## 📋 Prérequis

1. Compte Render.com (gratuit)
2. Repository GitHub avec le code du bot
3. Token Discord Bot
4. ID du serveur Discord

## 🔧 Configuration Render

### 1. Créer un nouveau Web Service

1. Allez sur [render.com](https://render.com)
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre repository GitHub `Gdiscord`
4. Configurez les paramètres :

```yaml
Name: gearted-discord-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### 2. Variables d'Environnement

Dans l'onglet **Environment** de votre service Render, ajoutez :

| Variable | Valeur |
|----------|--------|
| `BOT_TOKEN` | Votre token Discord (depuis Discord Developer Portal) |
| `GUILD_ID` | `1381740173234274364` |
| `PORT` | `10000` |

### 3. Configuration Auto-Deploy

- ✅ Activez **Auto-Deploy** pour déployer automatiquement les commits
- ✅ Sélectionnez la branche **main**

## 🚀 Déploiement

1. **Push vers GitHub :**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Render déploiera automatiquement** votre bot
3. **Surveillez les logs** dans le dashboard Render
4. **Testez les commandes** dans Discord une fois le déploiement terminé

## 📊 Monitoring

### Health Check
- **URL :** `https://votre-service.onrender.com/health`
- **Réponse :** `{"status": "healthy", "bot": "online"}`

### Logs
- Consultez les logs en temps réel dans le dashboard Render
- Surveillez les erreurs de connexion Discord
- Vérifiez les performances et l'utilisation mémoire

## 🎮 Test des Commandes

Une fois déployé, testez dans Discord :

```
!ping          # Test de connexion
!gstats        # Vos statistiques
!leaderboard   # Classement XP
!help_gearted  # Guide complet
!mylinks       # Liens formulaires
!update_my_roles # Mise à jour rôles
```

## 🔧 Résolution de Problèmes

### ❌ Bot Offline
- Vérifiez le token dans les variables d'environnement
- Consultez les logs pour les erreurs de connexion

### ❌ Commandes ne répondent pas
- Vérifiez que le bot a les bonnes permissions Discord
- Vérifiez l'ID du serveur (GUILD_ID)

### ❌ Service ne démarre pas
- Vérifiez les dépendances dans `requirements.txt`
- Consultez les logs de build pour les erreurs

## 💰 Coûts

- **Plan Gratuit Render :** Suffisant pour un bot Discord
- **Limitations :** Le service peut s'endormir après inactivité
- **Plan Payant :** Recommandé pour usage 24/7 intensif

## 🔄 Mises à Jour

Pour mettre à jour le bot :

1. Modifiez le code localement
2. Commitez et poussez vers GitHub
3. Render redéployera automatiquement
4. Surveillez les logs de déploiement

## 📈 Optimisations

- **Keep-Alive :** Endpoint `/health` maintient le service actif
- **Gestion d'erreurs :** Récupération automatique des pannes
- **Base de données :** Sauvegarde automatique des données XP

---

**🎯 Le bot est maintenant prêt pour la production !**
