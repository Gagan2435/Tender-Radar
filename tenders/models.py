from django.db import models


class Tender(models.Model):
    source = models.CharField(max_length=20)            # "ted" or "sample"
    ref = models.CharField(max_length=60)               # publication number on the source
    title = models.CharField(max_length=500)
    buyer = models.CharField(max_length=300, blank=True)
    country = models.CharField(max_length=3, blank=True)
    cpv = models.CharField(max_length=8, blank=True)    # Common Procurement Vocabulary code
    nature = models.CharField(max_length=20, blank=True)
    published = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    url = models.CharField(max_length=300, blank=True)
    sector = models.CharField(max_length=40, blank=True)
    sector_source = models.CharField(max_length=10, blank=True)  # "cpv" (from code) or "model" (predicted)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["source", "ref"], name="uniq_source_ref")]
        indexes = [models.Index(fields=["published"]), models.Index(fields=["sector"]),
                   models.Index(fields=["country"])]

    def __str__(self):
        return f"{self.ref}: {self.title[:60]}"
