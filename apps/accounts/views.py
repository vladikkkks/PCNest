from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Ласкаво просимо, {user.username}!')
            return redirect('catalog:list')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:list')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'catalog:list'
            return redirect(next_url)
        messages.error(request, 'Невірний логін або пароль.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('catalog:list')


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    from apps.builds.models import BuildLike
    builds = request.user.builds.prefetch_related('build_components__component', 'likes').all()
    liked_builds = (
        BuildLike.objects
        .filter(user=request.user)
        .select_related('build__user')
        .prefetch_related('build__build_components__component', 'build__likes')
        .order_by('-saved_at')
    )
    liked_builds = [bl.build for bl in liked_builds]
    tab = request.GET.get('tab', 'my')
    return render(request, 'accounts/profile.html', {
        'builds': builds,
        'liked_builds': liked_builds,
        'form': form,
        'tab': tab,
    })
