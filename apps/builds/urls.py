from django.urls import path
from . import views

app_name = 'builds'

urlpatterns = [
    path('',                                          views.build_create,          name='create'),
    path('<uuid:slug>/',                              views.build_detail,           name='detail'),
    path('<uuid:slug>/delete/',                       views.build_delete,           name='delete'),
    path('<uuid:slug>/add-component/',                views.build_add_component,    name='add_component'),
    path('<uuid:slug>/remove-component/<int:component_pk>/', views.build_remove_component, name='remove_component'),
]
