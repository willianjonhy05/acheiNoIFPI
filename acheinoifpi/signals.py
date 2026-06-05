from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Atividade, Categoria, Usuario, Local, Item


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
        
        
@receiver(post_save, sender=Item)
def criar_atividade_item(sender, instance, created, **kwargs):
    """
    Cria uma Atividade toda vez que um Item é criado
    ou seu status é alterado.
    """
    if created:
        # Item recém-criado
        Atividade.objects.create(
            titulo=f"Item cadastrado: {instance.nome or instance.codigo}",
            descricao=f"Um novo item foi registrado com status '{instance.get_status_display()}'.",
            cor="primary"
        )
    else:
        # Item existente atualizado: verificar mudança de status
        try:
            old_instance = Item.objects.get(pk=instance.pk)
        except Item.DoesNotExist:
            old_instance = None

        # Só cria atividade se o status mudou
        if old_instance and old_instance.status != instance.status:
            Atividade.objects.create(
                titulo=f"Status do item alterado: {instance.nome or instance.codigo}",
                descricao=f"O status do item mudou de '{old_instance.get_status_display()}' para '{instance.get_status_display()}'.",
                cor="info"
            )