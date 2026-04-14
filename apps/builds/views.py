from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.catalog.models import Component
from .models import Build, BuildComponent


@login_required
def build_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        component_ids = request.POST.getlist('components')
        if not name:
            messages.error(request, 'Вкажіть назву збірки.')
            return redirect('builds:create')
        if not component_ids:
            messages.error(request, 'Оберіть хоча б один компонент.')
            return redirect('builds:create')

        build = Build.objects.create(user=request.user, name=name)
        components = Component.objects.filter(pk__in=component_ids)
        for component in components:
            BuildComponent.objects.create(build=build, component=component)

        errors = build.check_compatibility()
        if errors:
            for err in errors:
                messages.warning(request, err)
        else:
            messages.success(request, 'Збірка збережена, сумісність підтверджена.')

        return redirect('builds:detail', slug=build.slug)

    components = Component.objects.all().order_by('type', 'name')
    return render(request, 'builds/create.html', {
        'components': components,
        'component_types': Component.Type.choices,
    })


def build_detail(request, slug):
    build = get_object_or_404(
        Build.objects.prefetch_related('build_components__component').select_related('user'),
        slug=slug
    )
    # Переглядати може будь-хто за прямим посиланням.
    errors = build.check_compatibility()
    context = {
        'build':       build,
        'total_price': build.get_total_price(),
        'errors':      errors,
    }
    return render(request, 'builds/detail.html', context)


@login_required
def build_delete(request, slug):
    build = get_object_or_404(Build, slug=slug, user=request.user)
    if request.method == 'POST':
        build.delete()
        messages.success(request, 'Збірку видалено.')
        return redirect('accounts:profile')
    return render(request, 'builds/confirm_delete.html', {'build': build})


@login_required
def build_add_component(request, slug):
    """AJAX — додати компонент до збірки."""
    if request.method == 'POST':
        build = get_object_or_404(Build, slug=slug, user=request.user)
        component_id = request.POST.get('component_id')
        component = get_object_or_404(Component, pk=component_id)
        _, created = BuildComponent.objects.get_or_create(build=build, component=component)
        errors = build.check_compatibility()
        return JsonResponse({
            'created': created,
            'total_price': str(build.get_total_price()),
            'errors': errors,
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def build_remove_component(request, slug, component_pk):
    """AJAX — видалити компонент зі збірки."""
    if request.method == 'POST':
        build = get_object_or_404(Build, slug=slug, user=request.user)
        BuildComponent.objects.filter(build=build, component_id=component_pk).delete()
        errors = build.check_compatibility()
        return JsonResponse({
            'total_price': str(build.get_total_price()),
            'errors': errors,
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)
