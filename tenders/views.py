from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from . import charts
from .models import Tender


def _filtered(request):
    qs = Tender.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(buyer__icontains=q))
    for f in ("sector", "country", "nature"):
        v = request.GET.get(f, "").strip()
        if v:
            qs = qs.filter(**{f: v})
    return qs


def _distinct(field):
    return list(Tender.objects.exclude(**{field: ""}).order_by(field).values_list(field, flat=True).distinct())


def dashboard(request):
    qs = _filtered(request).order_by("-published", "-id")
    params = request.GET.copy()
    params.pop("page", None)
    ctx = {"page": Paginator(qs, 25).get_page(request.GET.get("page")), "total": Tender.objects.count(),
           "shown": qs.count(), "params": params.urlencode(), "q": request.GET.get("q", ""),
           "sel": {k: request.GET.get(k, "") for k in ("sector", "country", "nature")},
           "sectors": _distinct("sector"), "countries": _distinct("country"), "natures": _distinct("nature")}
    return render(request, "tenders/dashboard.html", ctx)


def _grouped(request, field, limit=None):
    rows = _filtered(request).order_by().values(field).annotate(n=Count("id")).order_by("-n")
    rows = list(rows[:limit] if limit else rows)
    return [r[field] for r in rows], [r["n"] for r in rows]


def chart_sector(request):
    labels, values = _grouped(request, "sector")
    return HttpResponse(charts.bar_png(labels, values, "Tenders by sector"), content_type="image/png")


def chart_country(request):
    labels, values = _grouped(request, "country", 10)
    return HttpResponse(charts.bar_png(labels, values, "Top 10 buyer countries"), content_type="image/png")


def chart_daily(request):
    rows = (_filtered(request).exclude(published=None).order_by().values("published")
            .annotate(n=Count("id")).order_by("published"))
    xs, ys = [r["published"] for r in rows], [r["n"] for r in rows]
    return HttpResponse(charts.line_png(xs, ys, "Tenders published per day"), content_type="image/png")


def api_tenders(request):
    """Small JSON REST endpoint: /api/tenders/?q=cloud&country=DEU"""
    qs = _filtered(request).order_by("-published", "-id")
    rows = list(qs[:50].values("ref", "title", "buyer", "country", "sector", "published", "deadline", "url"))
    return JsonResponse({"count": qs.count(), "results": rows})
