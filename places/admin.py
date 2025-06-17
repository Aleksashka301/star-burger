from django.contrib import admin
from .models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['address', 'latitude', 'longitude']
    search_fields = ['address']
    readonly_fields = ['updated_at']
