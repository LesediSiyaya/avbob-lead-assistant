#!/bin/bash
# ============================================================
#  AVBOB Lead Assistant — GitHub Push Script
#  Run this ONCE from inside the avbob-lead-assistant folder
#  Usage: bash push_to_github.sh
# ============================================================

set -e   # exit on any error

# ── Colours ───────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; GOLD='\033[0;33m'; NC='\033[0m'

echo ""
echo -e "${GOLD}🤝  AVBOB Lead Assistant — GitHub Setup${NC}"
echo "=================================================="
echo ""

# ── Step 1: Collect inputs ────────────────────────────────────
echo -e "${BLUE}Step 1 of 4 — GitHub credentials${NC}"
echo ""
echo "You need a GitHub Personal Access Token."
echo "Get one here (takes 60 seconds):"
echo ""
echo -e "  ${YELLOW}https://github.com/settings/tokens/new${NC}"
echo ""
echo "Settings to use:"
echo "  • Note:        AVBOB Lead Assistant"
echo "  • Expiration:  90 days (or No expiration)"
echo "  • Scopes:      ✅ repo   (tick the top-level 'repo' checkbox)"
echo ""
echo "Then paste the token below (it won't be shown as you type)."
echo ""

read -p "GitHub username: " GH_USER
echo ""
read -s -p "Personal Access Token (paste, press Enter): " GH_TOKEN
echo ""
echo ""
read -p "Repository name [avbob-lead-assistant]: " REPO_NAME
REPO_NAME="${REPO_NAME:-avbob-lead-assistant}"
echo ""
read -p "Make repo private? [Y/n]: " PRIVATE_CHOICE
PRIVATE_CHOICE="${PRIVATE_CHOICE:-Y}"
if [[ "$PRIVATE_CHOICE" =~ ^[Yy]$ ]]; then
  PRIVATE="true"
  PRIVACY_LABEL="private"
else
  PRIVATE="false"
  PRIVACY_LABEL="public"
fi

echo ""
echo -e "${BLUE}Step 2 of 4 — Creating ${PRIVACY_LABEL} GitHub repository${NC}"
echo ""

# ── Step 2: Create the GitHub repo via API ────────────────────
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: token ${GH_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -d "{\"name\":\"${REPO_NAME}\",\"private\":${PRIVATE},\"description\":\"AI-powered Facebook lead assistant for AVBOB funeral insurance consultants\"}" \
  "https://api.github.com/user/repos")

HTTP_CODE=$(echo "$CREATE_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | head -1)

if [ "$HTTP_CODE" = "201" ]; then
  echo -e "  ${GREEN}✅  Repository created: https://github.com/${GH_USER}/${REPO_NAME}${NC}"
elif [ "$HTTP_CODE" = "422" ]; then
  echo -e "  ${YELLOW}⚠️  Repository already exists — continuing with existing repo${NC}"
else
  echo -e "  ${RED}❌  Failed to create repo (HTTP $HTTP_CODE)${NC}"
  echo "     Response: $RESPONSE_BODY"
  echo ""
  echo "Check your token has 'repo' scope and your username is correct."
  exit 1
fi

echo ""
echo -e "${BLUE}Step 3 of 4 — Initialising git and committing files${NC}"
echo ""

# ── Step 3: Git init and commit ───────────────────────────────
if [ ! -d ".git" ]; then
  git init
  echo -e "  ${GREEN}✅  Git initialised${NC}"
else
  echo -e "  ${GREEN}✅  Git already initialised${NC}"
fi

# Set remote (overwrite if exists)
git remote remove origin 2>/dev/null || true
git remote add origin "https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${REPO_NAME}.git"
echo -e "  ${GREEN}✅  Remote set${NC}"

# Stage all files
git add -A
echo -e "  ${GREEN}✅  Files staged${NC}"

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo -e "  ${YELLOW}⚠️  Nothing new to commit — pushing existing commits${NC}"
else
  git commit -m "🤝 Initial commit — AVBOB Lead Assistant

- Chrome Extension (Manifest V3)
- FastAPI backend with AI lead scoring
- SQLite CRM database
- OpenAI + Ollama support
- WhatsApp link generator
- Multilingual support (11 SA languages)
- Railway + Render deployment configs"
  echo -e "  ${GREEN}✅  Committed${NC}"
fi

echo ""
echo -e "${BLUE}Step 4 of 4 — Pushing to GitHub${NC}"
echo ""

# ── Step 4: Push ──────────────────────────────────────────────
git branch -M main
git push -u origin main --force

echo ""
echo "=================================================="
echo -e "${GOLD}🎉  All done!${NC}"
echo ""
echo -e "  ${GREEN}Repository:${NC}  https://github.com/${GH_USER}/${REPO_NAME}"
echo -e "  ${GREEN}Clone URL:${NC}   https://github.com/${GH_USER}/${REPO_NAME}.git"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Next step → Deploy to Railway:${NC}"
echo ""
echo "  1. Go to:  https://railway.app"
echo "  2. New Project → Deploy from GitHub"
echo "  3. Select:  ${REPO_NAME}"
echo "  4. Settings → Root Directory → type:  backend"
echo "  5. Variables → add:  OPENAI_API_KEY = sk-proj-..."
echo "  6. Networking → Generate Domain → copy your URL"
echo "  7. Open Chrome → chrome://extensions/ → Load unpacked → select extension/"
echo "  8. Click AVBOB icon → Settings → paste Railway URL → Save"
echo ""
echo -e "${GOLD}Full deploy guide: see DEPLOY.md${NC}"
echo "=================================================="
