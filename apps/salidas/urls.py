from django.urls import path

from . import views

app_name = 'salidas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('crear/', views.crear, name='crear'),
    path('<int:pk>/anular/', views.anular, name='anular'),
]
