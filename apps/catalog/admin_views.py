from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.accounts.decorators import admin_required
from .models import Component
from .forms import ComponentForm, ComponentSpecForm


@admin_required
def admin_component_list(request):
    components = Component.objects.all().order_by('type', 'name')
    return render(request, 'catalog/admin/list.html', {'components': components})


@admin_required
def admin_component_create(request):
    form      = ComponentForm(request.POST or None, request.FILES or None)
    spec_form = ComponentSpecForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and spec_form.is_valid():
        component = form.save()
        spec = spec_form.save(commit=False)
        spec.component = component
        spec.save()
        messages.success(request, f'Компонент «{component.name}» додано.')
        return redirect('catalog:admin_list')
    return render(request, 'catalog/admin/form.html', {
        'form': form, 'spec_form': spec_form, 'action': 'Додати'
    })


@admin_required
def admin_component_edit(request, pk):
    component = get_object_or_404(Component, pk=pk)
    spec      = getattr(component, 'spec', None)
    form      = ComponentForm(request.POST or None, request.FILES or None, instance=component)
    spec_form = ComponentSpecForm(request.POST or None, instance=spec)
    if request.method == 'POST' and form.is_valid() and spec_form.is_valid():
        form.save()
        spec = spec_form.save(commit=False)
        spec.component = component
        spec.save()
        messages.success(request, f'Компонент «{component.name}» оновлено.')
        return redirect('catalog:admin_list')
    return render(request, 'catalog/admin/form.html', {
        'form': form, 'spec_form': spec_form, 'action': 'Редагувати'
    })


@admin_required
def admin_component_delete(request, pk):
    component = get_object_or_404(Component, pk=pk)
    if request.method == 'POST':
        name = component.name
        component.delete()
        messages.success(request, f'Компонент «{name}» видалено.')
        return redirect('catalog:admin_list')
    return render(request, 'catalog/admin/confirm_delete.html', {'component': component})
