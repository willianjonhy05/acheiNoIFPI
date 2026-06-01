from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Atividade, Categoria, Usuario, Local


@receiver(post_save, sender=Usuario, dispatch_uid="registrar_atividade_usuario")
def registrar_atividade_usuario(sender, instance, created, raw, **kwargs):
    if raw:
        return

    if created:
        Atividade.objects.create(
            titulo="Novo usuário cadastrado",
            descricao=f"O usuário {instance.nome or instance.email} foi cadastrado no sistema.",
            cor="primary"
        )
    else:
        Atividade.objects.create(
            titulo="Usuário atualizado",
            descricao=f"Os dados do usuário {instance.nome or instance.email} foram atualizados.",
            cor="info"
        )


@receiver(post_save, sender=Categoria, dispatch_uid="registrar_atividade_categoria")
def registrar_atividade_categoria(sender, instance, created, raw, **kwargs):
    if raw:
        return

    if created:
        Atividade.objects.create(
            titulo="Nova categoria criada",
            descricao=f"A categoria {instance.nome} foi cadastrada com o código {instance.codigo}.",
            cor="success"
        )
    else:
        Atividade.objects.create(
            titulo="Categoria atualizada",
            descricao=f"A categoria {instance.nome} foi atualizada.",
            cor="warning"
        )
        
@receiver(post_save, sender=Local, dispatch_uid="registrar_atividade_local")
def registrar_atividade_local(sender, instance, created, raw, **kwargs):
    if raw:
        return

    if created:
        Atividade.objects.create(
            titulo="Novo local criado",
            descricao=f"O local {instance.nome} foi cadastrado no sistema.",
            cor="success"
        )
    else:
        Atividade.objects.create(
            titulo="Local atualizado",
            descricao=f"O local {instance.nome} foi atualizado.",
            cor="warning"
        )