from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('categorias/', include('apps.categorias.urls')),
    path('materiales/', include('apps.materiales.urls')),
    path('entradas/', include('apps.entradas.urls')),
    path('salidas/', include('apps.salidas.urls')),
    path('historial/', include('apps.historial.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('', include('apps.usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
