from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .utils import aluno_required, servidor_required, admin_required



def redirecionar_usuario(request, usuario):
    if usuario.is_superuser:
        return redirect("admin:index")
        # Se quiser mandar para o admin real do Django, use:
        # return redirect("admin:index")

    tipo = getattr(usuario, "tipo", None)

    if tipo == 1:
        return redirect("dashboard_aluno")

    if tipo == 2:
        return redirect("dashboard_servidor")

    messages.error(request, "Tipo de usuário inválido.")
    return redirect("entrar")

def home(request):
    return render(request, "public/em_construcao.html")


def novo_usuario(request):
    return render(request, "admin/novo_usuario.html")


def login_usuario(request):
    if request.user.is_authenticated:
        return redirecionar_usuario(request, request.user)

    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=email,
            password=password
        )

        if usuario is not None:
            if not usuario.is_active:
                messages.error(request, "Este usuário está inativo.")
                return redirect("entrar")

            auth_login(request, usuario)

            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(next_url)

            return redirecionar_usuario(request, usuario)

        messages.error(request, "E-mail ou senha inválidos.")
        return redirect("entrar")

    return render(request, "admin/login.html", {
        "next_url": next_url,
    })
    
    
def logout_usuario(request):
    logout(request)
    messages.success(request, "Você saiu do sistema com segurança.")
    return redirect("entrar")

def dashboard(request):
    return render(request, 'admin/dashboard.html')

@aluno_required
def dashboard_aluno(request):
    return render(request, "aluno/dashboard.html")


@servidor_required
def dashboard_servidor(request):
    return render(request, "servidor/dashboard.html")


@admin_required
def dashboard_admin(request):
    return render(request, "admin/dashboard.html")