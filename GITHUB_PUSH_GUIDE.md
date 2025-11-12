# Push to GitHub for Render Deployment

## Current Status

✅ **Files committed successfully!**
- Server code committed
- Secrets are properly ignored (.env, config.env in .gitignore)
- Ready to push to GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `examshield-license-server` (or any name)
3. Description: "ExamShield License Server - Backend API"
4. **Visibility:** Private (recommended) or Public
5. **DO NOT** initialize with README, .gitignore, or license
6. Click **Create repository**

## Step 2: Push to GitHub

Run these commands:

```powershell
# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/examshield-license-server.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Or if you prefer SSH:**
```powershell
git remote add origin git@github.com:YOUR_USERNAME/examshield-license-server.git
git push -u origin main
```

## Step 3: Verify Push

Check GitHub:
- All server files should be visible
- `.env` and `config.env` should NOT be visible (properly ignored)
- `data/` and `backups/` should NOT be visible

## Step 4: Deploy to Render

See `DEPLOY_TO_RENDER.md` for complete Render deployment instructions.

### Quick Render Setup:

1. Go to https://render.com
2. **New +** → **Web Service**
3. Connect GitHub repository
4. Select your repository
5. Configure:
   - **Root Directory:** `server`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python license_server.py`
6. Add environment variables (see DEPLOY_TO_RENDER.md)
7. Deploy!

## Important Notes

### Repository Structure for Render

Your repo structure:
```
examshield-license-server/
├── server/
│   ├── license_server.py
│   ├── requirements.txt
│   ├── register.html
│   ├── payment.html
│   ├── admin_dashboard.html
│   ├── success.html
│   └── ...
├── .gitignore
├── vercel.json
└── build_examshield_full.sh
```

**For Render:**
- Set **Root Directory:** `server`
- This tells Render to run commands from `server/` directory

### Environment Variables

**DO NOT commit these to GitHub:**
- `.env` files (already in .gitignore ✅)
- `config.env` (already in .gitignore ✅)
- Any files with secrets

**Set in Render Dashboard:**
- SMTP credentials
- WEBHOOK_SECRET
- ADMIN_SECRET
- Razorpay keys

### Data Persistence

For `license_db.json` to persist:
- Render free tier: Data is ephemeral (lost on restart)
- **Solution:** Use Render persistent disk OR use external database
- See `DEPLOY_TO_RENDER.md` for disk setup

## Troubleshooting

### Push Fails
```powershell
# If remote already exists
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO.git
git push -u origin main
```

### Authentication Issues
- Use GitHub Personal Access Token
- Or set up SSH keys
- Or use GitHub Desktop

### Files Not Showing on GitHub
- Check `.gitignore` isn't blocking them
- Verify files are committed: `git log --name-only`
- Check if files are in correct directory

## Next Steps After Push

1. ✅ Verify all files are on GitHub
2. ✅ Deploy to Render (see DEPLOY_TO_RENDER.md)
3. ✅ Set environment variables in Render
4. ✅ Test deployment
5. ✅ Update client build with Render URL
6. ✅ Configure Razorpay webhook

## Quick Commands Reference

```powershell
# Check status
git status

# View commits
git log --oneline

# Check what's ignored
git check-ignore server/.env

# Push to GitHub
git push origin main

# View remote
git remote -v
```

---

**Ready to push! Run the git commands above to push to GitHub.** 🚀

