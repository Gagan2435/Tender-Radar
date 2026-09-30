"""Data sources. `fetch_ted` calls the public, keyless TED (EU tenders) JSON API - the same
backend the TED website uses. `sample_data` is a clearly-labelled synthetic offline fallback."""
import datetime as dt
import random
import time

import requests

TED_URL = "https://api.ted.europa.eu/v3/notices/search"
FULL = ["publication-number", "notice-title", "buyer-name", "buyer-country", "classification-cpv",
        "contract-nature", "publication-date", "deadline"]
CORE = ["publication-number", "notice-title", "buyer-name", "publication-date"]


def text(v):
    """TED returns multilingual objects like {"eng": ["Title"]}; prefer English, else any language."""
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return next((t for t in map(text, v) if t), "")
    if isinstance(v, dict):
        for k in ("eng", "ENG", "en"):
            if k in v:
                return text(v[k])
        return next((t for t in map(text, v.values()) if t), "")
    return ""


def first(v):
    return v[0] if isinstance(v, list) and v else ("" if isinstance(v, list) else v)


def parse_notice(n):
    pn = first(n.get("publication-number"))
    if not pn:
        return None
    return {"ref": str(pn), "title": text(n.get("notice-title")), "buyer": text(n.get("buyer-name")),
            "country": str(first(n.get("buyer-country")) or ""), "cpv": str(first(n.get("classification-cpv")) or ""),
            "nature": str(first(n.get("contract-nature")) or ""),
            "published": str(first(n.get("publication-date")) or "")[:10],
            "deadline": str(first(n.get("deadline")) or "")[:10],
            "url": f"https://ted.europa.eu/en/notice/-/detail/{pn}"}


def _paginate(query, fields, max_items, log):
    out, token = [], None
    while len(out) < max_items:
        body = {"query": query, "fields": fields, "limit": min(100, max_items - len(out)),
                "scope": "ALL", "paginationMode": "ITERATION"}
        if token:
            body["iterationNextToken"] = token
        r = requests.post(TED_URL, json=body, timeout=45, headers={"User-Agent": "tender-radar-student-project"})
        if r.status_code >= 400:
            if out:
                break  # keep what we already have
            r.raise_for_status()
        d = r.json()
        notices = d.get("notices", [])
        out += [p for p in map(parse_notice, notices) if p]
        log(f"  fetched {len(out)} notices (TED reports {d.get('totalNoticeCount', '?')} matching)")
        token = d.get("iterationNextToken")
        if not token or not notices:
            break
        time.sleep(0.5)  # be polite to a public API
    return out[:max_items]


def fetch_ted(days=14, max_items=200, log=print):
    since = (dt.date.today() - dt.timedelta(days=days)).strftime("%Y%m%d")
    for query, fields in [(f"publication-date>={since}", FULL), (f"PD>={since}", FULL),
                          (f"publication-date>={since}", CORE)]:
        try:
            recs = _paginate(query, fields, max_items, log)
            if recs:
                return recs
        except requests.HTTPError as e:
            log(f"  TED rejected '{query}' ({e.response.status_code}): {e.response.text[:120]}")
    raise RuntimeError("TED returned no usable notices")


# ---------------------------------------------------------------- offline synthetic data
_T = {
    "72": ["Cloud hosting services for {x}", "Software development and maintenance for {x}", "Cybersecurity audit services",
           "IT support and helpdesk services", "Data centre modernisation", "Mobile app and website development"],
    "45": ["Construction of a new building for {x}", "Road resurfacing works", "Bridge repair and renovation works",
           "Renovation of school buildings", "Water pipeline construction works"],
    "33": ["Supply of medical devices for {x}", "Pharmaceuticals supply framework", "Laboratory diagnostic equipment",
           "Surgical instruments and consumables", "Ambulance vehicles and medical equipment"],
    "09": ["Solar power plant installation", "Supply of electricity for public buildings", "Energy efficiency retrofit",
           "Wind farm maintenance services", "Heating fuel supply for {x}"],
    "60": ["Bus fleet leasing services", "Railway track maintenance", "Passenger shuttle services",
           "Supply of electric buses", "Public transport ticketing system"],
    "90": ["Waste collection and disposal services", "Wastewater treatment plant operation", "Street cleaning services",
           "Recycling facility upgrade", "Environmental impact assessment services"],
    "80": ["Vocational training services", "School textbooks supply", "E-learning platform for schools",
           "University laboratory training courses", "Language training courses for staff"],
    "79": ["Consulting services for public administration", "Legal advisory services", "Marketing and communication campaign",
           "Audit and accounting services", "Recruitment and staffing services"],
}
_X = ["the municipality", "the regional hospital", "the ministry", "the university", "the city council"]
_PRE = ["", "Tender for ", "Provision of ", "Framework agreement for "]
_C = ["DEU", "FRA", "ESP", "ITA", "POL", "NLD", "SWE", "PRT"]


def sample_data(n=160, seed=42):
    rnd, today, rows = random.Random(seed), dt.date.today(), []
    for i in range(n):
        code = rnd.choice(list(_T))
        title = rnd.choice(_PRE) + rnd.choice(_T[code]).format(x=rnd.choice(_X))
        pub = today - dt.timedelta(days=rnd.randint(0, 13))
        c = rnd.choice(_C)
        rows.append({"ref": f"SAMPLE-{i:04d}", "title": title[:1].upper() + title[1:],
                     "buyer": f"Public buyer {c}-{rnd.randint(1, 30)}", "country": c, "cpv": code + "000000",
                     "nature": rnd.choice(["works", "services", "supplies"]), "published": pub.isoformat(),
                     "deadline": (pub + dt.timedelta(days=30)).isoformat(), "url": ""})
    return rows
