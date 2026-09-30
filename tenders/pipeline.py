"""Cleaning + loading. Pure functions first (testable without Django); DB work imports models lazily."""
import datetime as dt
import re

from .classifier import NaiveBayes, cpv_sector


def _date(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def _sp(s):
    return re.sub(r"\s+", " ", s or "").strip()


def clean(rec):
    """Normalise one raw record; return None if it is unusable."""
    title, ref = _sp(rec.get("title")), _sp(rec.get("ref"))
    if len(title) < 5 or not ref:
        return None
    cpv = re.sub(r"\D", "", rec.get("cpv") or "")[:8]
    sector = cpv_sector(cpv)
    return {"ref": ref[:60], "title": title[:500], "buyer": _sp(rec.get("buyer"))[:300],
            "country": _sp(rec.get("country")).upper()[:3], "cpv": cpv, "nature": _sp(rec.get("nature")).lower()[:20],
            "published": _date(rec.get("published")), "deadline": _date(rec.get("deadline")),
            "url": _sp(rec.get("url"))[:300], "sector": sector or "", "sector_source": "cpv" if sector else ""}


def ingest(records, source):
    """Insert records, skipping duplicates (unique on source+ref). Returns (new, duplicates, rejected)."""
    from .models import Tender
    new = dup = bad = 0
    for r in records:
        c = clean(r)
        if not c:
            bad += 1
            continue
        ref = c.pop("ref")
        _, created = Tender.objects.get_or_create(source=source, ref=ref, defaults=c)
        new += created
        dup += not created
    return new, dup, bad


def classify_missing():
    """Train on rows whose sector came from a CPV code, then predict a sector for rows that have none."""
    from .models import Tender
    labeled = list(Tender.objects.filter(sector_source="cpv").values_list("title", "sector"))
    todo = list(Tender.objects.filter(sector=""))
    if not labeled or not todo:
        return 0
    nb = NaiveBayes().fit([t for t, _ in labeled], [s for _, s in labeled])
    for t in todo:
        t.sector, t.sector_source = nb.predict(t.title), "model"
        t.save(update_fields=["sector", "sector_source"])
    return len(todo)
