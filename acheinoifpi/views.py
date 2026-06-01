from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .utils import aluno_required, servidor_required, admin_required, limpar_cpf
from .models import Usuario, Categoria, Atividade
from django.db import IntegrityError
from django.core.exceptions import ValidationError

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


def nova_categoria(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()

        erros = []

        if not nome:
            erros.append("Nome da categoria é obrigatório.")

        if len(nome) > 25:
            erros.append("O nome da categoria deve ter no máximo 25 caracteres.")

        if erros:
            for erro in erros:
                messages.error(request, erro)

            return render(request, "admin/nova_categoria.html", {
                "form_data": request.POST
            })

        try:
            categoria = Categoria(
                nome=nome,
                descricao=descricao or None,
                ativa=True
            )

            categoria.save()

            messages.success(
                request,
                f"Categoria '{categoria.nome}' cadastrada com sucesso. Código gerado: {categoria.codigo}."
            )

            return redirect("admin-dashboard")

        except ValidationError as erro:
            if hasattr(erro, "message_dict"):
                for campo, mensagens in erro.message_dict.items():
                    for mensagem in mensagens:
                        messages.error(request, mensagem)
            else:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)

        except IntegrityError:
            messages.error(
                request,
                "Erro ao salvar categoria. Já existe uma categoria com código ou slug semelhante."
            )

    return render(request, "admin/nova_categoria.html")

def novo_usuario(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        cpf = limpar_cpf(request.POST.get("cpf"))
        data_nascimento = request.POST.get("data_nascimento") or None
        email = request.POST.get("email", "").strip().lower()
        matricula = request.POST.get("matricula", "").strip()
        foto = request.FILES.get("foto")

        erros = []

        if not nome:
            erros.append("Nome completo é obrigatório.")

        if not cpf:
            erros.append("CPF é obrigatório.")
        elif len(cpf) != 11:
            erros.append("CPF inválido. Informe os 11 dígitos.")

        if not data_nascimento:
            erros.append("Data de nascimento é obrigatória.")

        if not email:
            erros.append("E-mail é obrigatório.")

        if not matricula:
            erros.append("Matrícula é obrigatória.")

        if email and Usuario.objects.filter(email=email).exists():
            erros.append("Já existe um usuário cadastrado com este e-mail.")

        if cpf and Usuario.objects.filter(cpf=cpf).exists():
            erros.append("Já existe um usuário cadastrado com este CPF.")

        if erros:
            for erro in erros:
                messages.error(request, erro)

            return render(request, "admin/novo_usuario.html", {
                "form_data": request.POST
            })

        try:
            usuario = Usuario(
                nome=nome,
                cpf=cpf,
                data_nascimento=data_nascimento,
                email=email,
                matricula=matricula,
                tipo=1,
                ativo=True,
            )

            if foto:
                usuario.foto = foto

            usuario.save()

            messages.success(request, "Usuário cadastrado com sucesso.")
            return redirect("admin-dashboard")

        except IntegrityError:
            messages.error(request, "Erro ao salvar. Verifique se CPF ou e-mail já estão cadastrados.")

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
    qtde_usuarios = Usuario.objects.count()
    usuarios = Usuario.objects.all()[:5]  # Exemplo: pegar os 5 usuários mais recentes
    atividades = Atividade.objects.all()[:3]
    
    context = {
        "qtde_usuarios": qtde_usuarios,
        "usuarios": usuarios,
        "atividades": atividades
    }
    
    return render(request, 'admin/dashboard.html', context)

@aluno_required
def dashboard_aluno(request):
    return render(request, "aluno/dashboard.html")


@servidor_required
def dashboard_servidor(request):
    return render(request, "servidor/dashboard.html")


@admin_required
def dashboard_admin(request):
    return render(request, "admin/dashboard.html")