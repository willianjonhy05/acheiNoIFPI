from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .utils import limpar_cpf, limpar_telefone, buscar_objeto_ativo_por_id, paginar_queryset
from .decorators import aluno_required, servidor_required, admin_required, usuario_required
from .models import Usuario, Categoria, Atividade, Local, Item
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q, Count
from .forms import UsuarioPasswordResetForm
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)



def redirecionar_usuario(request, usuario):
    if usuario.is_superuser:
        return redirect("admin:index")
        # Se quiser mandar para o admin real do Django, use:
        # return redirect("admin:index")

    tipo = getattr(usuario, "tipo", None)

    if tipo == 1:
        return redirect("dashboard-aluno")

    if tipo == 2:
        return redirect("admin-dashboard")

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

    # 🔥 usando sua função de paginação
    page_obj = paginar_queryset(request, categorias, por_pagina=10)

    context = {
        "categorias": page_obj,  # já pode iterar direto no template
        "page_obj": page_obj,
        "termo": termo,
    }

    return render(request, "admin/listar_categorias.html", context)


@servidor_required
def listar_locais(request):
    termo = request.GET.get("q", "").strip()

    locais = Local.objects.all().order_by("nome")

    if termo:
        locais = locais.filter(
            Q(nome__icontains=termo) |
            Q(predio__icontains=termo)
        )

    # 🔥 usando sua função de paginação
    page_obj = paginar_queryset(request, locais, por_pagina=10)

    context = {
        "locais": page_obj,  # já pode iterar direto no template
        "page_obj": page_obj,
        "termo": termo,
    }

    return render(request, "admin/listar_locais.html", context)


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
def alterar_status_local(request, codigo):
    local = get_object_or_404(Local, codigo=codigo)

    local.ativa = not local.ativa
    local.save(update_fields=["ativa"])

    if local.ativa:
        messages.success(request, f'Local "{local.nome}" ativado com sucesso.')
    else:
        messages.success(request, f'Local "{local.nome}" desativado com sucesso.')

    return redirect("listar-locais")


@servidor_required
@require_POST
def editar_local(request, codigo):
    local = get_object_or_404(Local, codigo=codigo)

    local.nome = request.POST.get("nome")
    local.predio = request.POST.get("predio")
    local.andar = request.POST.get("andar")
    local.telefone = request.POST.get("telefone")
    local.descricao = request.POST.get("descricao")

    local.sala_de_aula = True if request.POST.get("sala_de_aula") == "on" else False
    local.laboratorio = True if request.POST.get("laboratorio") == "on" else False

    local.save()

    return redirect(request.POST.get("next", "listar-locais"))

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

            return redirect("listar-locais")

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
def cadastrar_item_encontrado(request):
    categorias = Categoria.objects.filter(ativa=True).order_by("nome")
    locais = Local.objects.filter(ativa=True).order_by("nome")

    context = {
        "categorias": categorias,
        "locais": locais,
        "form_data": {},
        "categoria_selecionada": "",
        "local_selecionado": "",
    }

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        categoria_id = request.POST.get("categoria", "").strip()
        local_id = request.POST.get("local", "").strip()
        tamanho = request.POST.get("tamanho", "").strip()
        cor = request.POST.get("cor", "").strip()
        material = request.POST.get("material", "").strip()
        marca_modelo = request.POST.get("marca_modelo", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        foto = request.FILES.get("foto")

        context.update({
            "form_data": request.POST,
            "categoria_selecionada": categoria_id,
            "local_selecionado": local_id,
        })

        categoria = buscar_objeto_ativo_por_id(Categoria, categoria_id)

        local = None
        if local_id:
            local = buscar_objeto_ativo_por_id(Local, local_id)

        erros = []

        if not titulo:
            erros.append("O título do objeto é obrigatório.")

        if not categoria:
            erros.append("Selecione uma categoria válida.")

        if not tamanho:
            erros.append("O tamanho do objeto é obrigatório.")

        if not cor:
            erros.append("A cor do objeto é obrigatória.")

        if local_id and not local:
            erros.append("Selecione um local válido.")

        if erros:
            for erro in erros:
                messages.error(request, erro)

            return render(request, "admin/cadastrar_objeto_encontrado.html", context)

        Item.objects.create(
            nome=titulo,
            categoria=categoria,
            local=local,
            tamanho=tamanho,
            cor=cor,
            material=material,
            marca_ou_modelo=marca_modelo,
            descricao=descricao,
            foto=foto,
            status=2,

            # Usuário autenticado
            usuario_registro=request.user,
        )

        messages.success(request, "Objeto encontrado cadastrado com sucesso.")
        return redirect("listar-itens")

    return render(request, "admin/cadastrar_objeto_encontrado.html", context)

@servidor_required
def listar_usuarios(request):

    pesquisa = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "").strip()

    # 🔥 QUERY BASE COM ESTATÍSTICAS DOS ITENS
    usuarios = Usuario.objects.annotate(
        quantidade_itens=Count("usuario_registro", distinct=True),

        perdidos=Count(
            "usuario_registro",
            filter=Q(usuario_registro__status=1)
        ),

        encontrados=Count(
            "usuario_registro",
            filter=Q(usuario_registro__status=2)
        ),

        devolvidos=Count(
            "usuario_registro",
            filter=Q(usuario_registro__status=3)
        ),

        outros=Count(
            "usuario_registro",
            filter=Q(usuario_registro__status=4)
        ),
    ).order_by("nome")

    # 🔍 FILTRO DE BUSCA
    if pesquisa:
        usuarios = usuarios.filter(
            Q(nome__icontains=pesquisa) |
            Q(email__icontains=pesquisa) |
            Q(username__icontains=pesquisa) |
            Q(matricula__icontains=pesquisa) |
            Q(cpf__icontains=pesquisa)
        )

    # 🎯 FILTRO POR TIPO
    if tipo in ["1", "2"]:
        usuarios = usuarios.filter(tipo=int(tipo))

    # 📄 PAGINAÇÃO
    page_obj = paginar_queryset(request, usuarios, por_pagina=10)

    context = {
        "usuarios": page_obj,
        "page_obj": page_obj,
        "pesquisa": pesquisa,
        "tipo_selecionado": tipo,
    }

    return render(request, "admin/listar_usuarios.html", context)

def itens_encontrados(request):
    return render(request, "admin/itens_encontrados.html")

@usuario_required
def cadastrar_pedido_de_busca(request):
    categorias = Categoria.objects.filter(ativa=True).order_by("nome")
    locais = Local.objects.filter(ativa=True).order_by("nome")
    
    context = {
        "categorias": categorias,
        "locais": locais,
        "form_data": {},
        "categoria_selecionada": "",
        "local_selecionado": "",
    }
    
    
    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        categoria_id = request.POST.get("categoria", "").strip()
        local_id = request.POST.get("local", "").strip()
        tamanho = request.POST.get("tamanho", "").strip()
        cor = request.POST.get("cor", "").strip()
        material = request.POST.get("material", "").strip()
        marca_modelo = request.POST.get("marca_modelo", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        foto = request.FILES.get("foto")

        context.update({
            "form_data": request.POST,
            "categoria_selecionada": categoria_id,
            "local_selecionado": local_id,
        })

        categoria = buscar_objeto_ativo_por_id(Categoria, categoria_id)

        local = None
        if local_id:
            local = buscar_objeto_ativo_por_id(Local, local_id)

        erros = []

        if not titulo:
            erros.append("O título do objeto é obrigatório.")

        if not categoria:
            erros.append("Selecione uma categoria válida.")

        if not tamanho:
            erros.append("O tamanho do objeto é obrigatório.")

        if not cor:
            erros.append("A cor do objeto é obrigatória.")

        if local_id and not local:
            erros.append("Selecione um local válido.")

        if erros:
            for erro in erros:
                messages.error(request, erro)

            return render(request, "usuarios/cadastrar_pedido_de_busca.html", context)

        Item.objects.create(
            nome=titulo,
            categoria=categoria,
            local=local,
            tamanho=tamanho,
            cor=cor,
            material=material,
            marca_ou_modelo=marca_modelo,
            descricao=descricao,
            foto=foto,
            status=1,

            # Usuário autenticado
            usuario_registro=request.user,
            dono = request.user,
        )

        messages.success(request, "Objeto encontrado cadastrado com sucesso.")
        return redirect("meus-pedidos-de-busca")    
    

    
    return render(request, "usuarios/cadastrar_pedido_de_busca.html", context)

@usuario_required
def meus_pedidos_de_busca(request):
    pedidos = Item.objects.filter(
        dono=request.user
    ).order_by("-data_registro")

    return render(request, "usuarios/meus_pedidos_de_busca.html", {
        "pedidos": pedidos
    })


@servidor_required
def dashboard(request):
    qtde_usuarios = Usuario.objects.count()
    qtde_itens_encontrados = Item.objects.filter(status=2).count()
    qtde_itens_devolvidos = Item.objects.filter(status=3).count()
    usuarios = Usuario.objects.all()[:5]  
    atividades = Atividade.objects.all()[:3]
    
    context = {
        "qtde_usuarios": qtde_usuarios,
        "qtde_itens_encontrados": qtde_itens_encontrados,
        "qtde_itens_devolvidos": qtde_itens_devolvidos,
        "usuarios": usuarios,
        "atividades": atividades
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def meu_perfil(request):
    return render(request, "admin/perfil.html", {
        "usuario": request.user
    })
    
    
@login_required
def atualizar_perfil(request):
    usuario = request.user

    if request.method == "POST":
        usuario.telefone = request.POST.get("telefone")
        usuario.matricula = request.POST.get("matricula")

        # FOTO (upload seguro)
        if "foto" in request.FILES:
            usuario.foto = request.FILES["foto"]

        usuario.save()

        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("meu-perfil")

    return redirect("meu-perfil")

@aluno_required
def dashboard_aluno(request):
    return render(request, "admin/dashboard_aluno.html")


@servidor_required
def dashboard_servidor(request):
    return render(request, "admin/dashboard_servidor.html")


@servidor_required
def dashboard_admin(request):
    return render(request, "admin/dashboard.html")


class EsqueciMinhaSenhaView(PasswordResetView):
    template_name = "usuarios/esqueci_minha_senha.html"
    email_template_name = "usuarios/emails/redefinir_senha_email.html"
    subject_template_name = "usuarios/emails/redefinir_senha_assunto.txt"
    success_url = reverse_lazy("senha-reset-enviada")
    form_class = UsuarioPasswordResetForm
    extra_context = {
        "titulo": "Recuperar senha"
    }


class SenhaResetEnviadaView(PasswordResetDoneView):
    template_name = "usuarios/senha_reset_enviada.html"


class RedefinirSenhaView(PasswordResetConfirmView):
    template_name = "usuarios/redefinir_senha.html"
    success_url = reverse_lazy("senha-reset-finalizada")

    def form_valid(self, form):
        response = super().form_valid(form)

        if hasattr(self.user, "senha_alterada"):
            self.user.senha_alterada = True
            self.user.save(update_fields=["senha_alterada"])

        return response


class SenhaResetFinalizadaView(PasswordResetCompleteView):
    template_name = "usuarios/senha_reset_finalizada.html"
    
    
    
    
@servidor_required
def listar_itens(request):

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    itens = Item.objects.select_related(
        "usuario_registro",
        "categoria"
    ).all().order_by("-data_registro")

    if search:
        itens = itens.filter(
            Q(nome__icontains=search) |
            Q(codigo__icontains=search) |
            Q(marca_ou_modelo__icontains=search) |
            Q(cor__icontains=search) |
            Q(tamanho__icontains=search)
        )

    if status in ["1", "2", "3", "4"]:
        itens = itens.filter(status=int(status))

    if categoria:
        itens = itens.filter(categoria_id=categoria)

    page_obj = paginar_queryset(request, itens, por_pagina=10)

    context = {
        "itens": page_obj,
        "page_obj": page_obj,
        "search": search,
        "status_selecionado": status,
        "categoria_selecionada": categoria,
        "categorias": Categoria.objects.all(),
    }

    return render(request, "admin/listar_itens.html", context)


@servidor_required
def detalhe_item(request, codigo):

    item = get_object_or_404(
        Item.objects.select_related(
            "usuario_registro",
            "dono",
            "categoria",
            "local"
        ),
        codigo=codigo
    )

    if request.method == "POST":
        novo_status = request.POST.get("status")

        if novo_status in ["1", "2", "3", "4"]:
            item.status = int(novo_status)

            if int(novo_status) == 3:  # devolvido
                from django.utils import timezone
                item.data_devolucao = timezone.now()

            item.save()

            return redirect("detalhe-item", codigo=item.codigo)

    context = {
        "item": item,
        "status_choices": Item.STATUS
    }

    return render(request, "admin/detalhe_item.html", context)


@servidor_required
def itens_por_categoria(request, slug):

    categoria = get_object_or_404(Categoria, slug=slug)

    itens = Item.objects.select_related(
        "usuario_registro",
        "categoria"
    ).filter(
        categoria=categoria
    ).order_by("-data_registro")

    search = request.GET.get("q", "").strip()

    if search:
        itens = itens.filter(
            Q(nome__icontains=search) |
            Q(codigo__icontains=search) |
            Q(marca_ou_modelo__icontains=search) |
            Q(cor__icontains=search) |
            Q(tamanho__icontains=search)
        )

    page_obj = paginar_queryset(request, itens, por_pagina=10)

    context = {
        "categoria": categoria,
        "itens": page_obj,
        "page_obj": page_obj,
        "search": search,
    }

    return render(request, "admin/itens_por_categoria.html", context)


@servidor_required
def listar_atividades(request):
    termo = request.GET.get("q", "").strip()

    atividades = Atividade.objects.all().order_by("titulo")

    if termo:
        atividades = atividades.filter(
            Q(titulo__icontains=termo) |
            Q(descricao__icontains=termo)
        )

    # 🔥 usando sua função de paginação
    page_obj = paginar_queryset(request, atividades, por_pagina=10)

    context = {
        "atividades": page_obj,  # já pode iterar direto no template
        "page_obj": page_obj,
        "termo": termo,
    }

    return render(request, "admin/listar_atividades.html", context)
