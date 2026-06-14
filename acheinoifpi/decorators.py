from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, render, resolve_url


def aluno_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            login_url = resolve_url(settings.LOGIN_URL)
            return redirect_to_login(
                request.get_full_path(),
                login_url,
                REDIRECT_FIELD_NAME
            )

        if request.user.tipo == 1 or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        return render(request, "public/acesso_negado.html", status=403)

    return _wrapped_view


def servidor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            login_url = resolve_url(settings.LOGIN_URL)
            return redirect_to_login(
                request.get_full_path(),
                login_url,
                REDIRECT_FIELD_NAME
            )

        if request.user.tipo == 2 or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        return render(request, "public/acesso_negado.html", status=403)

    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            login_url = resolve_url(settings.LOGIN_URL)
            return redirect_to_login(
                request.get_full_path(),
                login_url,
                REDIRECT_FIELD_NAME
            )

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Acesso permitido apenas para administradores.")
        return render(request, "public/acesso_negado.html", status=403)

    return _wrapped_view


def usuario_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            login_url = resolve_url(settings.LOGIN_URL)
            return redirect_to_login(
                request.get_full_path(),
                login_url,
                REDIRECT_FIELD_NAME
            )

        if request.user.tipo == 1 or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        return render(request, "public/acesso_negado.html", status=403)

    return _wrapped_view