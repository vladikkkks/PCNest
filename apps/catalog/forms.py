from django import forms
from .models import Component, ComponentSpec


class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = [
            'name', 'type', 'brand', 'price', 'image',
            'image_alt',
            'socket', 'ram_type', 'wattage', 'description',
        ]


class ComponentSpecForm(forms.ModelForm):
    class Meta:
        model = ComponentSpec
        fields = ['manufacturer', 'release_year', 'warranty', 'extra']
