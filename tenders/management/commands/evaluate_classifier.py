from django.core.management.base import BaseCommand

from tenders import classifier
from tenders.models import Tender


class Command(BaseCommand):
    help = "Accuracy of the Naive Bayes sector classifier (title -> sector) on an 80/20 split."

    def handle(self, *args, **o):
        qs = Tender.objects.filter(sector_source="cpv")
        real = qs.filter(source="ted").count() >= 50
        rows = list((qs.filter(source="ted") if real else qs).order_by("id").values_list("title", "sector"))
        if len(rows) < 50:
            self.stdout.write("Not enough labelled tenders yet (need 50+). Run: python manage.py crawl")
            return
        r = classifier.evaluate(rows)
        self.stdout.write(f"Sector classifier on {'REAL TED data' if real else 'synthetic sample data'}: "
                          f"train={r['train']} test={r['test']} accuracy={r['accuracy']:.2f} "
                          f"(majority-class baseline {r['baseline']:.2f})")
