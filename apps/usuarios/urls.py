from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('usuarios/', views.lista, name='lista'),
    path('usuarios/crear/', views.crear, name='crear'),
    path('usuarios/<int:pk>/editar/', views.editar, name='editar'),
    path('usuarios/<int:pk>/eliminar/', views.eliminar, name='eliminar'),
]
