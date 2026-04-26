# Deployment Guide - Render.com (Free Tier)

## Prerequisites
- GitHub account with your project repository
- Render.com account (free tier)

## Step-by-Step Deployment

### 1. Prepare Your Project
✅ Already done! I've created:
- `wsgi.py` - Production entry point
- `Procfile` - Deployment configuration
- `runtime.txt` - Python version specification
- `.env.example` - Environment variables template
- Updated `requirements.txt` - Added gunicorn and psycopg2

### 2. Push Changes to GitHub
```bash
git add .
git commit -m "Add deployment configuration files"
git push origin main
```

### 3. Deploy to Render.com

#### Step A: Connect Your Repository
1. Go to https://render.com
2. Sign up or log in
3. Click "New +" → "Web Service"
4. Connect your GitHub repository (AI_Influencer)
5. Select the repository and click "Connect"

#### Step B: Configure the Web Service
1. **Name**: `ml-project` (or your preferred name)
2. **Environment**: `Python 3`
3. **Region**: Choose closest to your users
4. **Branch**: `main`
5. **Build Command**: 
   ```
   pip install -r requirements.txt
   ```
6. **Start Command**: 
   ```
   gunicorn wsgi:app
   ```

#### Step C: Add Environment Variables
In Render dashboard, go to "Environment" section and add:
```
SECRET_KEY=generate-a-random-secret-key-here
SECURITY_PASSWORD_SALT=generate-a-random-salt-here
FLASK_ENV=production
```

**To generate secure keys in Python:**
```python
import secrets
print(secrets.token_hex(32))  # For SECRET_KEY
print(secrets.token_hex(16))  # For SECURITY_PASSWORD_SALT
```

#### Step D: Add PostgreSQL Database (Optional but Recommended)
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Create a database instance
3. Copy the connection string
4. Add to environment variable: `DATABASE_URL=<connection-string>`

### 4. Monitoring
- Check logs in Render dashboard
- Monitor in Render → Your Service → Logs tab

## Important Notes

### Free Tier Limitations
- ⏸️ Service spins down after 15 min of inactivity (free tier)
- 📦 Limited to 0.5GB RAM
- 🌐 Shared resources
- ❌ No custom domains (free tier)

### Troubleshooting

**Issue: Module not found errors**
- Solution: Update requirements.txt and rebuild

**Issue: Database connection failed**
- Solution: Check DATABASE_URL in environment variables

**Issue: Static files not loading**
- Solution: Ensure static/ and templates/ directories are in git

**Issue: Service crashes on startup**
- Check logs: `Render Dashboard → Logs tab`

## Alternative Free Deployment Options

### Option 1: Railway.app
- Similar to Render
- 5$ free credit monthly
- URL: https://railway.app

### Option 2: Heroku (Limited Free - Being Phased Out)
- Dyno hours limited
- URL: https://www.heroku.com/

### Option 3: Replit
- Direct code editor integration
- Free tier available
- URL: https://replit.com/

## Rollback
If deployment fails:
1. Check the logs in Render dashboard
2. Fix the issue locally
3. Commit and push to GitHub
4. Render will auto-redeploy

## Production Checklist
- [ ] SECRET_KEY changed (not 'dev-secret-key...')
- [ ] SECURITY_PASSWORD_SALT changed
- [ ] Database configured (PostgreSQL recommended)
- [ ] All dependencies in requirements.txt
- [ ] FLASK_ENV set to 'production'
- [ ] Static files committed to git
- [ ] Tested locally with: `gunicorn wsgi:app`
- [ ] .env not committed to git (check .gitignore)

## Post-Deployment
1. Your app will be live at: `https://ml-project.onrender.com` (example)
2. Monitor performance in Render dashboard
3. Set up error notifications (optional in Render)
4. Keep dependencies updated regularly

## Need Help?
- Render Documentation: https://render.com/docs
- Flask Documentation: https://flask.palletsprojects.com/
- GitHub: Push changes, Render will auto-redeploy
