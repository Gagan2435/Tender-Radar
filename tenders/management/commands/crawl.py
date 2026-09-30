from django.core.management.base import BaseCommand, CommandError

from tenders import pipeline, sources


class Command(BaseCommand):
    help = "Crawl tenders (live TED API, or offline sample), clean, dedupe, load, classify."

    def add_arguments(self, p):
        p.add_argument("--source", default="auto", choices=["auto", "ted", "sample"])
        p.add_argument("--days", type=int, default=14)
        p.add_argument("--max", type=int, default=200)

    def handle(self, *args, **o):
        log, recs, used = self.stdout.write, None, "sample"
        if o["source"] in ("auto", "ted"):
            log("Crawling live EU tenders from the TED API ...")
            try:
                recs, used = sources.fetch_ted(o["days"], o["max"], log), "ted"
            except Exception as e:  # network down, API change, etc.
                if o["source"] == "ted":
                    raise CommandError(f"Live crawl failed: {e}")
                log(f"Live crawl failed ({e}).")
        if recs is None:
            recs, used = sources.sample_data(), "sample"
            log("Using bundled SYNTHETIC sample data (offline demo, not real tenders).")
        new, dup, bad = pipeline.ingest(recs, used)
        log(f"[{used}] fetched={len(recs)} new={new} duplicates_skipped={dup} rejected={bad}")
        log(f"sector predicted by model for {pipeline.classify_missing()} notices without a CPV code")
