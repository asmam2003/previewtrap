# previewtrap

A Flask-based OSINT server for attributing anonymous account activity across messaging platforms. Generates authentic-looking link previews on Telegram, Discord, Slack, WhatsApp, and iMessage while logging visitor metadata and device fingerprints when real users click through.

## Problem

Most IP-logging services (Grabify, IPLogger, Canarytokens) are blocked by major messaging platforms. Telegram, Discord, and others maintain blocklists of known tracker domains and refuse to generate link previews for them, making the links immediately suspicious. There is no single deployable tool that handles crawler detection, custom preview injection, IP logging, device fingerprinting, and redirect in one package.

## How It Works

previewtrap differentiates between crawler bots and real users at the User-Agent level:

- **Crawlers** (TelegramBot, Discordbot, Twitterbot, Slackbot, WhatsApp, facebookexternalhit, LinkedInBot, iMessageBot) receive a custom HTML page with configurable Open Graph metadata, generating an authentic link preview with controlled title, description, and image.
- **Real users** are logged and redirected to a configurable destination URL. From the user's perspective, they clicked a normal link.

## Data Captured

**Server-side:**
- IP address (with X-Forwarded-For handling for proxied deployments)
- Geolocation via ip-api.com (country, region, city, ISP, org, mobile/proxy/hosting flags)
- User-Agent string
- UTC timestamp

**Client-side (JavaScript fingerprinting):**
- Timezone and locale
- Screen resolution
- Device memory and CPU core count
- Battery level
- Canvas fingerprint
- WebGL renderer
- Connection type

**VPN detection:**
- Datacenter IP identification
- Known VPN ISP name matching
- Timezone-versus-IP-country mismatch scoring
- Composite VPN confidence score

## Deployment

Built for one-click deployment on Render, Railway, or any platform that supports Flask.

```bash
pip install -r requirements.txt
python app.py
```

### Environment Variables

| Variable         | Description                              | Default              |
|------------------|------------------------------------------|----------------------|
| `REDIRECT_URL`   | Where real users are sent after logging   | `https://airbnb.com` |
| `OG_TITLE`       | Link preview title                       | `Check this out`     |
| `OG_DESCRIPTION` | Link preview description                 |                      |
| `OG_IMAGE`       | Link preview image URL                   |                      |
| `OG_URL`         | URL shown in preview metadata            |                      |
| `LOG_FILE`       | Path to JSON log file                    | `logs.json`          |
| `PORT`           | Server port                              | `5000`               |

## Routes

| Route   | Description                        |
|---------|------------------------------------|
| `/`     | Main endpoint: serve preview or log and redirect |
| `/logs` | JSON log viewer (protect or remove in production) |

## Stack

Python, Flask, Gunicorn, ip-api.com

## Use Cases

- Sock-puppet and fake account attribution
- Anonymous harassment source identification
- Link-click verification in social engineering assessments
- Messaging platform OSINT collection

## Limitations

- Geolocation accuracy depends on ip-api.com and degrades behind VPNs (mitigated by VPN confidence scoring)
- JavaScript fingerprinting requires the user's browser to execute JS; some clients (e.g., in-app browsers) may limit available APIs
- Log storage is local JSON; not designed for high-volume production use
