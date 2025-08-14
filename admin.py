from django.contrib import admin
from .models import Event, RSVP

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title','date','location','is_private','created_by')
    search_fields = ('title','location')
    list_filter = ('is_private','date')

admin.site.register(RSVP)
