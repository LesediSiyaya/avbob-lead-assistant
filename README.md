# 🤝 AVBOB Lead Assistant

AI-powered Chrome Extension + FastAPI backend for AVBOB funeral insurance consultants.
Detects high-intent Facebook posts, scores leads, generates replies, and saves everything to a CRM.

---

## Folder Structure

```
avbob-lead-assistant/
├── extension/                  ← Chrome Extension (load this in Chrome)
│   ├── manifest.json
│   ├── content_script.js       ← Runs on Facebook, detects posts
│   ├── background.js           ← Service worker, API bridge
│   ├── popup.html / popup.js   ← Mini-CRM popup panel
│   ├── styles.css              ← Injected UI styles
│   └── icons/                  ← Auto-generated PNG icons
│
├── backend/                    ← FastAPI Python server
│   ├── main.py                 ← App entrypoint + HTML dashboard
│   ├── models.py               ← Pydantic request/response models
│   ├── database.py             ← SQLite CRUD layer
│   ├── requirements.txt
│   ├── .env.example
│   ├── ai/
│   │   ├── engine.py           ← OpenAI + Ollama AI calls
│   │   └── prompts.py          ← All prompt templates
│   └── routes/
│       ├── analyze.py          ← POST /analyze-lead
│       ├── replies.py          ← POST /generate-reply
│       ├── whatsapp.py         ← POST /whatsapp-link
│       └── leads.py            ← POST /save-lead  GET /get-leads  etc.
│
├── generate_icons.py           ← One-time icon generator
└── README.md
```

---

## Quick Start (15 minutes)

### Step 1 — Clone / download

```bash
# If using Git:
git clone <your-repo-url>
cd avbob-lead-assistant

# Or just unzip the folder you downloaded
```

### Step 2 — Generate icons

```bash
python3 generate_icons.py
# Creates extension/icons/icon16.png  icon48.png  icon128.png
```

### Step 3 — Set up the backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
```

### Step 4 — Run the backend

```bash
# Make sure you're in the backend/ folder with venv active
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
✅  Database ready: avbob_leads.db
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it: open http://localhost:8000/health in your browser.

### Step 5 — Load the Chrome Extension

1. Open Chrome → go to `chrome://extensions/`
2. Toggle **Developer mode** ON (top-right switch)
3. Click **Load unpacked**
4. Select the `extension/` folder (not the whole project — just `extension/`)
5. The 🤝 AVBOB icon appears in your toolbar

---

## Using the Extension on Facebook

### What happens automatically:
- Open any Facebook group or feed
- Scroll through posts
- Any post matching funeral cover keywords gets a **gold outline** and an AVBOB toolbar injected below it

### The 4 buttons:

| Button | What it does |
|---|---|
| 🤖 **Analyze** | Scores the lead 0–100, classifies intent, shows summary |
| ✍️ **Reply** | Generates a Facebook comment reply (copy and post manually) |
| 💬 **WhatsApp** | Generates a follow-up message + wa.me link (you click, you send) |
| 💾 **Save** | Saves the lead to your SQLite CRM via the backend |

> ⚠️ **Nothing is sent automatically.** Every action requires your review and manual action.

---

## CRM Dashboard

Open http://localhost:8000/dashboard to see all leads in a table with:
- Score and intent level
- Status (new / contacted / follow-up / converted)
- Language detected
- Links to original posts

Or use the extension popup (click the toolbar icon) to see recent leads and update statuses.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/analyze-lead` | Score + classify a post |
| POST | `/generate-reply` | Generate Facebook reply |
| POST | `/whatsapp-link` | Generate WhatsApp message + link |
| POST | `/save-lead` | Save lead to CRM |
| GET | `/get-leads` | Fetch all leads |
| POST | `/update-status/{id}` | Update lead status |
| GET | `/stats` | CRM statistics |
| GET | `/dashboard` | HTML CRM dashboard |

### Example API call:
```bash
curl -X POST http://localhost:8000/analyze-lead \
  -H "Content-Type: application/json" \
  -d '{"text": "Looking for AVBOB funeral cover for my family", "author": "Thabo M", "postUrl": "", "matched_keywords": ["funeral cover"]}'
```

---

## AI Configuration

### Option A — OpenAI (recommended)
1. Get an API key from platform.openai.com
2. Add to `.env`: `OPENAI_API_KEY=sk-proj-...`
3. Uses `gpt-4o-mini` by default (~$0.001 per analysis)

### Option B — Ollama (free, offline)
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. In `.env`: `USE_OLLAMA=true`
4. Quality may vary; llama3 or mistral recommended

---

## Deploy to Railway (cloud)

```bash
# From the backend/ folder
# 1. Push to GitHub
# 2. Connect repo to Railway (railway.app)
# 3. Set environment variables in Railway dashboard
# 4. Update extension's backend URL in the popup settings
```

---

## Example Workflow

```
1. Consultant opens Facebook → browses a funeral cover community group
2. Post detected: "Hi, my mom passed and we have no cover. Anyone know AVBOB prices?"
3. Gold outline appears around the post
4. Click 🤖 Analyze → Score: 91/100, HIGH intent
5. Click 💾 Save → Lead saved to CRM
6. Click ✍️ Reply → AI writes empathetic Facebook comment
7. Consultant reviews, edits if needed, copies, posts manually
8. Click 💬 WhatsApp → Message generated in same language as post
9. Consultant opens WhatsApp, finds the contact, pastes message, sends manually
10. Open popup → change status from "new" to "contacted"
```

---

## Compliance & Ethics

- ✅ **No auto-messaging** — every message requires manual copy-paste
- ✅ **No Facebook API bypass** — reads visible DOM only, like a human would
- ✅ **No scraping** — only processes posts the logged-in user can already see
- ✅ **Human-in-the-loop** — consultant reviews every AI suggestion
- ✅ **POPIA aware** — only saves publicly visible post data
- ✅ **Keyword matching** — only surfaces relevant posts, no bulk harvesting

---

## Troubleshooting

| Problem | Fix |
|---|---|
| No posts highlighted on Facebook | Scroll down to load posts; extension scans after 2.5s |
| "Cannot reach backend" error | Make sure `uvicorn` is running on port 8000 |
| AI returns fallback responses | Check your `OPENAI_API_KEY` in `.env` |
| Extension not loading | Make sure you selected the `extension/` folder, not the root |
| Icons missing | Run `python3 generate_icons.py` from the project root |
| CORS error in browser console | Backend is not running or URL mismatch in popup settings |
