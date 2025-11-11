# Push to GitHub - Quick Guide

## ✅ Your Code is Ready!

Files are committed and ready to push. Here's how to push to GitHub:

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `examshield-license-server`
3. **Visibility:** Private (recommended - contains business logic)
4. **DO NOT** check "Initialize with README"
5. Click **Create repository**

## Step 2: Push to GitHub

**Replace `YOUR_USERNAME` with your GitHub username:**

```powershell
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/examshield-license-server.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**If you get authentication error:**
- Use GitHub Personal Access Token (instead of password)
- Or use SSH: `git@github.com:YOUR_USERNAME/examshield-license-server.git`

## Step 3: Verify on GitHub

Check that these files are on GitHub:
- ✅ `server/license_server.py`
- ✅ `server/requirements.txt`
- ✅ `server/*.html` (register, payment, admin, success)
- ✅ `.gitignore`
- ✅ `vercel.json`

**Should NOT be on GitHub:**
- ❌ `server/.env` (secrets - properly ignored)
- ❌ `server/data/` (database - properly ignored)
- ❌ `server/venv/` (virtual environment - properly ignored)

## Step 4: Deploy to Render

After pushing to GitHub:

1. Go to https://render.com
2. Sign up / Sign in
3. **New +** → **Web Service**
4. Connect GitHub account
5. Select your repository: `examshield-license-server`
6. Configure:
   - **Name:** `examshield-license-server`
   - **Root Directory:** `server`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python license_server.py`
7. Add environment variables (see DEPLOY_TO_RENDER.md)
8. Click **Create Web Service**

## What Gets Deployed

**Only the backend server code:**
- License server API
- Registration page
- Payment page
- Admin dashboard
- Success page

**NOT deployed (stays private):**
- Client code (examshield.py, installer)
- Build scripts
- Documentation
- Test files

## After Deployment

1. Get your Render URL: `https://examshield-license-server.onrender.com`
2. Update `ES_VERIFY_URL` in client build:
   ```powershell
   $env:ES_VERIFY_URL="https://examshield-license-server.onrender.com/verify"
   ./build_examshield_full.sh
   ```
3. Build `.deb` package (contains only client code)
4. Distribute `.deb` to customers

## Repository Structure

```
examshield-license-server/ (GitHub)
├── server/              ← Deployed to Render
│   ├── license_server.py
│   ├── requirements.txt
│   ├── *.html
│   └── ...
├── .gitignore
└── vercel.json
```

**Customer gets:**
- Only the `.deb` package (Ubuntu installer)
- No backend code
- No server access
- Just the ExamShield application

## Quick Commands

```powershell
# Check what's committed
git ls-files

# Check what's ignored
git check-ignore server/.env server/data server/venv

# Push to GitHub
git push origin main

# View remote
git remote -v
```

---

**Ready to push! Run the commands in Step 2.** 🚀

