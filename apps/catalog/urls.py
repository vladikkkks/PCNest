from django.urls import path
from . import views, admin_views

app_name = 'catalog'

urlpatterns = [
    # Public
    path('',                        views.component_list,             name='list'),
    path('<int:pk>/',               views.component_detail,           name='detail'),

    # Admin panel
    path('admin/',                  admin_views.admin_component_list,   name='admin_list'),
    path('admin/create/',           admin_views.admin_component_create, name='admin_create'),
    path('admin/<int:pk>/edit/',    admin_views.admin_component_edit,   name='admin_edit'),
    path('admin/<int:pk>/delete/',  admin_views.admin_component_delete, name='admin_delete'),
]
