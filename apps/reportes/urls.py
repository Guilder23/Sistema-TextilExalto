from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('pdf/materiales/', views.pdf_materiales, name='pdf_materiales'),
    path('pdf/ventas/', views.pdf_ventas, name='pdf_ventas'),
]
