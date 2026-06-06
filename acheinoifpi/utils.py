from django.shortcuts import redirect
from django.contrib import messages
import re
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import render
import string
import random


def aluno_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == 1:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Acesso permitido apenas para alunos.")
        return redirect("login")

    return wrapper


def servidor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == 2:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Acesso permitido apenas para servidores.")
        return redirect("login")

    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Acesso permitido apenas para administradores.")
        return redirect("login")

    return wrapper

def limpar_cpf(cpf):
    return re.sub(r"\D", "", cpf or "")


def limpar_telefone(telefone):
    return re.sub(r"\D", "", telefone or "")



def servidor_required(view_func):
    """
    Permite acesso apenas para:
    - Usuários do tipo Servidor (tipo=2)
    - Superusuários (is_superuser=True)
    Se não autorizado, exibe página de 'Acesso negado'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.tipo == 2 or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        return render(request, "public/acesso_negado.html", status=403)
    return _wrapped_view


def usuario_required(view_func):
    """
    Permite acesso apenas para:
    - Usuários do tipo Aluno (tipo=1)
    - Superusuários (is_superuser=True)
    Se não autorizado, exibe página de 'Acesso negado'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.tipo == 1 or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        return render(request, "public/acesso_negado.html", status=403)
    return _wrapped_view



def gerar_codigo_aleatorio(length=6):
    """
    Gera um código aleatório com letras maiúsculas e números.
    Exemplo: 'A4B9C1'
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def buscar_objeto_ativo_por_id(modelo, id_objeto):
    if not id_objeto:
        return None

    try:
        return modelo.objects.filter(id=int(id_objeto), ativa=True).first()
    except (TypeError, ValueError):
        return None

