from django.contrib import admin
from .models import FamousPerson

@admin.register(FamousPerson)
class FamousPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'created_at')
    list_filter = ('difficulty',)
    search_fields = ('name',)
    ordering = ('name',)
