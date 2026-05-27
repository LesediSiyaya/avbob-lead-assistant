# ============================================================
#  Routes: /webhook/facebook
#  Receives real-time page post events from Facebook Graph API
#  and scores them as leads automatically.
#
#  Setup:
#   1. Create a Facebook Developer App at developers.facebook.com
#   2. Add the "Facebook Login for Business" product
#   3. Under Webhooks, subscribe to the "feed" field on your Page
#   4. Set the callback URL to:
#        https://zip-hub--lesedisiyaya.replit.app/webhook/facebook
#   5. Set your FB_VERIFY_TOKEN (any random string you choose)
#   6. Get a Page Access Token and set FB_PAGE_ACCESS_TOKEN
# ============================================================
import os
import logging
from fastapi           import APIRouter, Request, Response, HTTPException
from database          import insert_lead, lead_exists
from ai.engine         import analyze_lead

logger = logging.getLogger("avbob.facebook")
router = APIRouter(prefix="/webhook")

FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "")


# ── Webhook verification (Facebook sends this once on setup) ───
@router.get("/facebook", tags=["Facebook"])
def fb_verify(request: Request):
    mode      = request.query_params.get("hub.mode")
    token     = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if not FB_VERIFY_TOKEN:
        logger.error("FB_VERIFY_TOKEN is not set")
        raise HTTPException(status_code=500, detail="FB_VERIFY_TOKEN not configured")

    if mode == "subscribe" and token == FB_VERIFY_TOKEN:
        logger.info("Facebook webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")

    logger.warning("Facebook webhook verification failed — token mismatch")
    raise HTTPException(status_code=403, detail="Verification failed")


# ── Incoming post events ────────────────────────────────────────
@router.post("/facebook", tags=["Facebook"])
async def fb_events(request: Request):
    body = await request.json()

    if body.get("object") != "page":
        return {"status": "ignored", "reason": "not a page event"}

    saved = 0
    skipped = 0

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "feed":
                continue

            value = change.get("value", {})

            post_text = value.get("message", "").strip()
            if not post_text:
                skipped += 1
                continue

            if lead_exists(post_text):
                skipped += 1
                logger.info("Duplicate post — skipped")
                continue

            author      = value.get("from", {}).get("name", "Unknown")
            post_id     = value.get("post_id", "")
            permalink   = value.get("permalink_url", "")

            post_url = permalink or (
                f"https://www.facebook.com/{post_id.replace('_', '/posts/')}"
                if post_id else ""
            )

            try:
                analysis = await analyze_lead(
                    post_text        = post_text,
                    author           = author,
                    matched_keywords = [],
                )
                insert_lead(
                    name         = author if author != "Unknown" else None,
                    post_text    = post_text,
                    post_url     = post_url,
                    lead_score   = analysis["score"],
                    intent_level = analysis["intent"],
                    language     = analysis.get("language", "en"),
                )
                saved += 1
                logger.info("Lead saved from Facebook post by %s (score=%s)", author, analysis["score"])
            except Exception as exc:
                logger.error("Failed to process Facebook post: %s", exc)
                skipped += 1

    return {"status": "ok", "saved": saved, "skipped": skipped}
