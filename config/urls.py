from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import index

urlpatterns = [
    path('',          index),
    path('admin/',    admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('catalog/',  include('apps.catalog.urls')),
    path('builds/',   include('apps.builds.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
