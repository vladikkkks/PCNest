from django.shortcuts import render
from apps.builds.models import Build

def index(request):
    recent_builds = Build.objects.select_related("user").prefetch_related("build_components__component")[:9]
    return render(request, "home.html", {"recent_builds": recent_builds})
