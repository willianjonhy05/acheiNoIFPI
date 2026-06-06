from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .utils import aluno_required, servidor_required, admin_required, limpar_cpf, limpar_telefone
from .models import Usuario, Categoria, Atividade, Local
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Q

def redirecionar_usuario(request, usuario):
    if usuario.is_superuser:
        return redirect("admin:index")
        # Se quiser mandar para o admin real do Django, use:
        # return redirect("admin:index")

    tipo = getattr(usuario, "tipo", None)

    if tipo == 1:
        return redirect("dashboard-aluno")

    if tipo == 2:
        return redirect("dashboard_servidor")

    messages.error(request, "Tipo de usuário inválido.")
    return redirect("entrar")

def home(request):
    return render(request, "public/em_construcao.html")


@servidor_required
def listar_categorias(request):
    termo = request.GET.get("q", "").strip()

    categorias = Categoria.objects.all().order_by("nome")

    if termo:
        categorias = categorias.filter(
            Q(nome__icontains=termo) |
            Q(codigo__icontains=termo)
        )

    paginator = Paginator(categorias, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "categorias": page_obj.object_list,
        "page_obj": page_obj,
        "termo": termo,
    }

    return render(request, "admin/listar_categorias.html", context)


@servidor_required
def alterar_status_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)

    categoria.ativa = not categoria.ativa
    categoria.save(update_fields=["ativa"])

    if categoria.ativa:
        messages.success(request, f'Categoria "{categoria.nome}" ativada com sucesso.')
    else:
        messages.success(request, f'Categoria "{categoria.nome}" desativada com sucesso.')

    return redirect("listar_categorias")


@servidor_required
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

@servidor_required
def novo_usuario(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        cpf = limpar_cpf(request.POST.get("cpf"))
        telefone = limpar_telefone(request.POST.get("telefone"))
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
            
        if telefone and len(telefone) not in [10, 11]:
            erros.append("Telefone inválido. Informe o telefone com DDD.")  

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
                telefone=telefone
            )

            if foto:
                usuario.foto = foto

            usuario.save()

            messages.success(request, "Usuário cadastrado com sucesso.")
            return redirect("admin-dashboard")

        except IntegrityError:
            messages.error(request, "Erro ao salvar. Verifique se CPF ou e-mail já estão cadastrados.")

    return render(request, "admin/novo_usuario.html")

@servidor_required
def novo_servidor(request):

    locais = Local.objects.filter(ativa=True).order_by("nome")

    if request.method == "POST":

        nome = request.POST.get("nome", "").strip()
        cpf = limpar_cpf(request.POST.get("cpf"))
        telefone = limpar_telefone(request.POST.get("telefone"))
        data_nascimento = request.POST.get("data_nascimento") or None
        email = request.POST.get("email", "").strip().lower()
        local_selecionado = request.POST.get("local")
        matricula = request.POST.get("matricula", "").strip()
        foto = request.FILES.get("foto")

        erros = []
        local = None

        # Local de trabalho
        if local_selecionado:
            try:
                local = Local.objects.get(pk=int(local_selecionado))
            except (ValueError, Local.DoesNotExist):
                erros.append("Local de trabalho inválido.")
        else:
            erros.append("Selecione um local de trabalho.")

        # Nome
        if not nome:
            erros.append("Nome completo é obrigatório.")

        # CPF
        if not cpf:
            erros.append("CPF é obrigatório.")
        elif len(cpf) != 11:
            erros.append("CPF inválido. Informe os 11 dígitos.")

        # Data de nascimento
        if not data_nascimento:
            erros.append("Data de nascimento é obrigatória.")

        # E-mail
        if not email:
            erros.append("E-mail é obrigatório.")

        # Verificações de duplicidade
        if email and Usuario.objects.filter(email=email).exists():
            erros.append("Já existe um usuário cadastrado com este e-mail.")

        if cpf and Usuario.objects.filter(cpf=cpf).exists():
            erros.append("Já existe um usuário cadastrado com este CPF.")

        # Telefone
        if telefone and len(telefone) not in [10, 11]:
            erros.append("Telefone inválido. Informe o telefone com DDD.")

        if erros:
            for erro in erros:
                messages.error(request, erro)

            return render(
                request,
                "admin/novo_servidor.html",
                {
                    "form_data": request.POST,
                    "locais": locais,
                    "local_selecionado": (
                        int(local_selecionado)
                        if local_selecionado and local_selecionado.isdigit()
                        else None
                    ),
                },
            )

        try:
            usuario = Usuario(
                nome=nome,
                cpf=cpf,
                data_nascimento=data_nascimento,
                local=local,
                email=email,
                matricula=matricula,
                tipo=2,
                ativo=True,
                telefone=telefone,
            )

            if foto:
                usuario.foto = foto

            usuario.save()

            messages.success(
                request,
                "Servidor cadastrado com sucesso."
            )

            return redirect("admin-dashboard")

        except IntegrityError:
            messages.error(
                request,
                "Erro ao salvar. Verifique se CPF ou e-mail já estão cadastrados."
            )

            return render(
                request,
                "admin/novo_servidor.html",
                {
                    "form_data": request.POST,
                    "locais": locais,
                    "local_selecionado": (
                        int(local_selecionado)
                        if local_selecionado and local_selecionado.isdigit()
                        else None
                    ),
                },
            )

    return render(
        request,
        "admin/novo_servidor.html",
        {
            "locais": locais,
            "local_selecionado": None,
        },
    )
    
    
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


@servidor_required    
def novo_local(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        predio = request.POST.get("predio", "").strip()
        andar = request.POST.get("andar", "").strip()
        telefone = limpar_telefone(request.POST.get("telefone"))
        descricao = request.POST.get("descricao", "").strip()

        sala_de_aula = request.POST.get("sala_de_aula") == "on"
        laboratorio = request.POST.get("laboratorio") == "on"

        erros = []

        if not nome:
            erros.append("Nome do local é obrigatório.")

        if len(nome) > 25:
            erros.append("O nome do local deve ter no máximo 25 caracteres.")

        if not predio:
            erros.append("Prédio é obrigatório.")

        if len(predio) > 5:
            erros.append("O prédio deve ter no máximo 5 caracteres.")

        if not andar:
            erros.append("Andar é obrigatório.")

        if len(andar) > 5:
            erros.append("O andar deve ter no máximo 5 caracteres.")

        if telefone and len(telefone) not in [10, 11]:
            erros.append("Telefone inválido. Informe o telefone com DDD.")

        if erros:
            for erro in erros:
                messages.error(request, erro)

            return render(request, "admin/novo_local.html", {
                "form_data": request.POST
            })

        try:
            local = Local(
                nome=nome,
                predio=predio,
                andar=andar,
                telefone=telefone,
                descricao=descricao or None,
                sala_de_aula=sala_de_aula,
                laboratorio=laboratorio,
                ativa=True
            )

            local.save()

            messages.success(
                request,
                f"Local '{local.nome}' cadastrado com sucesso. Código gerado: {local.codigo}."
            )

            return redirect(request.path)

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
                "Erro ao salvar local. Já existe um local com código semelhante."
            )

    return render(request, "admin/novo_local.html")
    

@login_required
def alterar_senha(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            usuario = form.save()
            usuario.senha_alterada = True
            usuario.save(update_fields=["senha_alterada"])
            update_session_auth_hash(request, usuario)

            messages.success(request, "Senha alterada com sucesso.")
            return redirect(request.path)

        messages.error(request, "Corrija os erros abaixo para alterar sua senha.")

    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "admin/alterar_senha.html", {
        "form": form
    })

    
def logout_usuario(request):
    logout(request)
    messages.success(request, "Você saiu do sistema com segurança.")
    return redirect("entrar")


@servidor_required
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


def meu_perfil(request):
    return render(request, "admin/meu_perfil.html")

@aluno_required
def dashboard_aluno(request):
    return render(request, "admin/dashboard_aluno.html")


@servidor_required
def dashboard_servidor(request):
    return render(request, "admin/dashboard_servidor.html")


@admin_required
def dashboard_admin(request):
    return render(request, "admin/dashboard.html")