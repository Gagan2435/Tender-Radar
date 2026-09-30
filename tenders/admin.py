from django.contrib import admin

from .models import Tender


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ("ref", "title", "country", "sector", "published")
    search_fields = ("title", "buyer")
    list_filter = ("sector", "country", "source")
