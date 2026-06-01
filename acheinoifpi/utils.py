from django.shortcuts import redirect
from django.contrib import messages
import re

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