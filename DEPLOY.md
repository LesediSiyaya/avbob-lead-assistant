# AVBOB Lead Assistant — Deployment Guide

## What You're Deploying

```
Chrome Extension (your browser)
        │  HTTP requests
        ▼
FastAPI Backend (Railway cloud server)
        │
        ├── Claude / OpenAI  (AI scoring & reply generation)
        └── SQLite database  (lead CRM — persisted on disk)
```

The extension runs **locally in your Chrome browser**.
The backend runs **in the cloud** so it's always available.

---

## PART 1 — Deploy the Backend to Railway

Railway is the simplest option: free to start, no credit card required, deploys from GitHub in under 3 minutes.

---

### Step 1 — Get a free Railway account

1. Go to **railway.app**
2. Click **Login → Login with GitHub**
3. Authorise Railway to access your GitHub

---

### Step 2 — Push the backend to GitHub

Open your terminal in the project folder:

```bash
# Navigate into the project
cd avbob-lead-assistant

# Initialise git (if not done already)
git init
git add .
git commit -m "Initial commit — AVBOB Lead Assistant"
```

Now create a new GitHub repository:

1. Go to **github.com** → click **New repository**
2. Name it: `avbob-lead-assistant`
3. Set to **Private** (recommended — contains your API keys later)
4. **Do NOT** tick "Add README" (you already have one)
5. Click **Create repository**

GitHub will show you the push commands. Run them:

```bash
git remote add origin https://github.com/YOUR_USERNAME/avbob-lead-assistant.git
git branch -M main
git push -u origin main
```

---

### Step 3 — Create a Railway project

1. Go to **railway.app/dashboard**
2. Click **New Project**
3. Choose **Deploy from GitHub repo**
4. Select `avbob-lead-assistant`
5. Railway asks which folder to deploy — click **Add Service → GitHub Repo**

> ⚠️ Railway deploys the **root** of the repo by default.
> You need to tell it to use the `backend/` subfolder.

6. Click the service → go to **Settings** tab
7. Under **Source**, set **Root Directory** to: `backend`
8. Click **Save**
9. Railway will redeploy automatically

---

### Step 4 — Set environment variables

In Railway, click your service → **Variables** tab → **New Variable**:

Add these one by one:

| Variable | Value |
|---|---|
| `OPENAI_API_KEY` | `sk-proj-...` (your OpenAI key from platform.openai.com) |
| `OPENAI_MODEL` | `gpt-4o-mini` |
| `USE_OLLAMA` | `false` |
| `DB_PATH` | `/app/avbob_leads.db` |

Click **Deploy** after adding variables.

---

### Step 5 — Get your backend URL

1. In Railway, click your service → **Settings** tab
2. Under **Networking**, click **Generate Domain**
3. You'll get a URL like: `https://avbob-lead-assistant-production.up.railway.app`

**Test it** — open this in your browser:
```
https://YOUR-RAILWAY-URL.up.railway.app/health
```

You should see:
```json
{"status": "ok", "service": "AVBOB Lead Assistant", "version": "1.0.0"}
```

✅ Backend is live.

---

## PART 2 — Install the Chrome Extension

---

### Step 6 — Generate icons (one time only)

```bash
cd avbob-lead-assistant
python3 generate_icons.py
```

---

### Step 7 — Load the extension in Chrome

1. Open Chrome and go to: `chrome://extensions/`
2. Toggle **Developer mode** ON (top-right corner)
3. Click **Load unpacked**
4. Browse to your project folder and select the **`extension/`** subfolder
5. The 🤝 AVBOB icon appears in your Chrome toolbar

---

### Step 8 — Connect the extension to your deployed backend

1. Click the 🤝 AVBOB icon in Chrome toolbar
2. Click **⚙️ Settings & Backend URL** at the bottom
3. Replace `http://localhost:8000` with your Railway URL:
   ```
   https://avbob-lead-assistant-production.up.railway.app
   ```
4. Click **Save**
5. The status dot should turn **green** — Connected

---

## PART 3 — Test the Full System

### Step 9 — Test on Facebook

1. Open **facebook.com** in Chrome
2. Go to any group or search for "funeral cover"
3. Scroll through posts
4. Any post mentioning funeral cover, AVBOB, burial policy, etc. gets a **gold outline** and toolbar

Click each button:
- 🤖 **Analyze** → should return score + intent within 3 seconds
- ✍️ **Reply** → generates a comment suggestion
- 💬 **WhatsApp** → generates a wa.me link
- 💾 **Save** → saves lead, button turns green ✅

### Step 10 — Check the CRM dashboard

Open in your browser:
```
https://YOUR-RAILWAY-URL.up.railway.app/dashboard
```

You should see your saved leads in the table.

---

## Alternative: Deploy to Render (also free)

If you prefer Render over Railway:

1. Go to **render.com** → sign up with GitHub
2. Click **New → Web Service**
3. Connect your `avbob-lead-assistant` GitHub repo
4. Set **Root Directory** to `backend`
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Choose **Free** plan
8. Under **Environment Variables**, add your `OPENAI_API_KEY`
9. Under **Disks**, add a disk:
   - Name: `avbob-data`
   - Mount Path: `/data`
   - Size: 1 GB
10. Update `DB_PATH` env var to: `/data/avbob_leads.db`
11. Click **Create Web Service**

> ⚠️ Render free tier **spins down after 15 minutes of inactivity**.
> First request after sleep takes ~30 seconds. Railway stays awake.

---

## Keeping the Extension Updated

When you change backend URL or update the code:

**Backend changes:**
```bash
git add .
git commit -m "Update backend"
git push
# Railway/Render auto-deploys on push
```

**Extension changes:**
- Edit files in `extension/`
- Go to `chrome://extensions/`
- Click the **refresh icon** on the AVBOB extension card

---

## Cost

| Service | Cost |
|---|---|
| Railway Starter | Free ($5 credit/month — covers ~500 hrs) |
| Render Free | Free (sleeps after inactivity) |
| OpenAI gpt-4o-mini | ~$0.001 per analysis (1000 analyses = $1) |
| Chrome Extension | Free (developer mode) |
| **Total typical month** | **$0 – $5** |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Status dot stays red | Check Railway logs — likely missing `OPENAI_API_KEY` env var |
| "Cannot reach backend" in extension | Verify Railway URL in extension popup settings. Make sure no trailing `/` |
| Posts not getting gold outline on Facebook | Reload the Facebook tab after loading extension. Scroll slowly. |
| AI returns generic/fallback responses | `OPENAI_API_KEY` env var is wrong or has no credit |
| Railway deploy fails | Check that **Root Directory** is set to `backend` in Railway settings |
| 422 error in Railway logs | Pydantic validation error — check request format. Open Railway logs tab. |
| Database resets on Railway restart | Add a Railway Volume: Settings → Volumes → Mount at `/app` → set `DB_PATH=/app/avbob_leads.db` |

---

## Adding a Railway Persistent Volume (Recommended)

By default, Railway's filesystem resets on redeploy. To keep leads permanently:

1. Railway dashboard → your service → **Volumes** tab
2. Click **Create Volume**
3. Mount path: `/app/data`
4. Go to **Variables** → set `DB_PATH` = `/app/data/avbob_leads.db`
5. Redeploy

Your SQLite database now persists across all deployments and restarts.

---

## Security Checklist Before Going Live

- [ ] Set `OPENAI_API_KEY` only in Railway/Render — never in code
- [ ] Keep GitHub repo **Private**
- [ ] Do not commit `.env` file (already in `.gitignore`)
- [ ] Optionally add a simple API key to the backend (see below)

### Optional: Add a basic API key to the backend

Add to `.env` / Railway vars:
```
API_SECRET_KEY=your-random-secret-here
```

Add to `backend/main.py` before the routers:
```python
from fastapi import Header, HTTPException

async def verify_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_SECRET_KEY", ""):
        raise HTTPException(status_code=403, detail="Invalid API key")
```

Then add `dependencies=[Depends(verify_key)]` to each router include.

---

## Summary of URLs After Deployment

| URL | Purpose |
|---|---|
| `https://YOUR-APP.up.railway.app/health` | Health check |
| `https://YOUR-APP.up.railway.app/dashboard` | CRM dashboard |
| `https://YOUR-APP.up.railway.app/docs` | Auto-generated API docs |
| `chrome://extensions/` | Manage your Chrome extension |
