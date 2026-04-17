from django.contrib import admin
from .models import Component, ComponentSpec


class ComponentSpecInline(admin.StackedInline):
    model = ComponentSpec
    extra = 1


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'type', 'brand', 'price', 'socket', 'ram_type', 'wattage')
    list_filter   = ('type', 'brand', 'ram_type')
    search_fields = ('name', 'brand')
    inlines       = [ComponentSpecInline]
