from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from acheinoifpi.views import login_usuario, dashboard, alterar_status_categoria, listar_categorias, meu_perfil, novo_servidor, logout_usuario, home, novo_usuario, nova_categoria, novo_local, alterar_senha, dashboard_aluno, dashboard_servidor

urlpatterns = [
    path("adm/", admin.site.urls),
    path("entrar/", login_usuario, name="entrar"),
    path("logout/", logout_usuario, name="logout"),
    
    # 1º A rota mais longa/específica (usuarios/novo) ANTES da rota geral
    path("dashboard/usuarios/novo/", novo_usuario, name="novo-usuario"),
    path("dashboard/servidores/novo/", novo_servidor, name="novo-servidor"),
    path("dashboard/categorias/", listar_categorias, name="listar_categorias"),
    path("dashboard/categorias/novo/", nova_categoria, name="nova-categoria"),
    path("dashboard/categorias/<slug:slug>/alterar-status/", alterar_status_categoria, name="alterar-status-categoria"),
    path("dashboard/locais/novo/", novo_local, name="novo-local"),
    path("dashboard/perfil/alterar-senha/", alterar_senha, name="alterar_senha"),
    
    path("dashboard/aluno/", dashboard_aluno, name="dashboard-aluno"),
    path("dashboard/servidor/", dashboard_servidor, name="dashboard-servidor"),
    
    # 2º A rota mais curta do dashboard depois
    path("dashboard/perfil/", meu_perfil, name="meu-perfil"),
    path("dashboard/", dashboard, name="admin-dashboard"),
    
    # 3º A raiz do site por último
    path("", home, name="home"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)