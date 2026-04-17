from django.contrib import admin
from .models import Component, ComponentSpec


class ComponentSpecInline(admin.StackedInline):
    model = ComponentSpec
    extra = 1


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'type', 'brand', 'price', 'has_real_photo', 'socket', 'ram_type', 'wattage')
    list_filter   = ('type', 'brand', 'ram_type')
    search_fields = ('name', 'brand')
    readonly_fields = ('image_source', 'has_real_photo', 'image_updated_at')
    inlines       = [ComponentSpecInline]
