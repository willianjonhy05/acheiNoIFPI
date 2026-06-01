from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from acheinoifpi.views import login_usuario, dashboard, logout_usuario, home, novo_usuario

urlpatterns = [
    path("adm/", admin.site.urls),
    path("entrar/", login_usuario, name="entrar"),
    path("logout/", logout_usuario, name="logout"),
    
    # 1º A rota mais longa/específica (usuarios/novo) ANTES da rota geral
    path("dashboard/usuarios/novo/", novo_usuario, name="novo-usuario"),
    
    # 2º A rota mais curta do dashboard depois
    path("dashboard/", dashboard, name="admin-dashboard"),
    
    # 3º A raiz do site por último
    path("", home, name="home"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)