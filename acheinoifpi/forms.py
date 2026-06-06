from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm


class UsuarioPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        UserModel = get_user_model()
        email_field_name = UserModel.get_email_field_name()

        usuarios = UserModel._default_manager.filter(
            **{
                f"{email_field_name}__iexact": email,
                "is_active": True,
                "ativo": True,
            }
        )

        for usuario in usuarios:
            email_usuario = getattr(usuario, email_field_name)

            if (
                usuario.has_usable_password()
                and email_usuario
                and email_usuario.casefold() == email.casefold()
            ):
                yield usuario