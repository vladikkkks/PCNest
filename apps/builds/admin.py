from django.contrib import admin
from .models import Build, BuildComponent


class BuildComponentInline(admin.TabularInline):
    model = BuildComponent
    extra = 0


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    inlines      = [BuildComponentInline]
