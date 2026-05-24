from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .utils import aluno_required, servidor_required, admin_required


def home(request):
    return render(request, "public/em_construcao.html")


def login_usuario(request):
    if request.user.is_authenticated:
        if request.user.tipo == 1:
            return redirect("dashboard_aluno")
        elif request.user.tipo == 2:
            return redirect("dashboard_servidor")
        elif request.user.is_superuser:
            return redirect("dashboard_admin")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.POST.get("next")

        usuario = authenticate(
            request,
            username=email,
            password=password
        )

        if usuario is not None:
            if not usuario.is_active:
                messages.error(request, "Este usuário está inativo.")
                return redirect("login")

            login(request, usuario)

            if next_url:
                return redirect(next_url)

            if usuario.is_superuser:
                return redirect("dashboard_admin")

            if usuario.tipo == 1:
                return redirect("dashboard_aluno")

            if usuario.tipo == 2:
                return redirect("dashboard_servidor")

            messages.error(request, "Tipo de usuário inválido.")
            return redirect("login")

        else:
            messages.error(request, "E-mail ou senha inválidos.")
            return redirect("login")

    return render(request, "admin/login.html")

def logout_usuario(request):
    logout(request)
    messages.success(request, "Você saiu do sistema com segurança.")
    return redirect("login")

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