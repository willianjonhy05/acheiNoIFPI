from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Local, Usuario, Categoria, Item


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nome",
        "predio",
        "andar",
        "telefone",
        "sala_de_aula",
        "laboratorio",
        "ativa",
    )

    list_filter = (
        "ativa",
        "sala_de_aula",
        "laboratorio",
        "predio",
        "andar",
    )

    search_fields = (
        "codigo",
        "nome",
        "predio",
        "andar",
        "telefone",
    )

    readonly_fields = (
        "codigo",
    )

    ordering = (
        "predio",
        "andar",
        "nome",
    )

    fieldsets = (
        ("Identificação do local", {
            "fields": (
                "codigo",
                "nome",
                "predio",
                "andar",
            )
        }),
        ("Contato e descrição", {
            "fields": (
                "telefone",
                "descricao",
            )
        }),
        ("Classificação", {
            "fields": (
                "sala_de_aula",
                "laboratorio",
                "ativa",
            )
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nome",
        "slug",
        "ativa",
    )

    list_filter = (
        "ativa",
    )

    search_fields = (
        "codigo",
        "nome",
        "slug",
    )

    readonly_fields = (
        "codigo",
        "slug",
    )

    ordering = (
        "nome",
    )

    fieldsets = (
        ("Dados da categoria", {
            "fields": (
                "codigo",
                "nome",
                "slug",
                "descricao",
                "ativa",
            )
        }),
    )


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = (
        "email",
        "username",
        "nome",
        "tipo",
        "local",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "tipo",
        "local",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
    )

    search_fields = (
        "email",
        "username",
        "nome",
        "cpf",
        "matricula",
        "setor",
    )

    ordering = (
        "email",
    )

    readonly_fields = (
        "criado_em",
        "last_login",
        "date_joined",
    )

    fieldsets = (
        ("Dados de acesso", {
            "fields": (
                "email",
                "username",
                "password",
            )
        }),
        ("Informações pessoais", {
            "fields": (
                "nome",
                "cpf",
                "data_nascimento",
                "foto",
            )
        }),
        ("Perfil no sistema", {
            "fields": (
                "tipo",
                "matricula",
                "setor",
                "local",
                "ativo",
            )
        }),
        ("Permissões do Django", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Datas importantes", {
            "fields": (
                "last_login",
                "date_joined",
                "criado_em",
            )
        }),
    )

    add_fieldsets = (
        ("Dados de acesso", {
            "classes": (
                "wide",
            ),
            "fields": (
                "email",
                "username",
                "nome",
                "cpf",
                "tipo",
                "matricula",
                "setor",
                "local",
                "password1",
                "password2",
            ),
        }),
        ("Permissões", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
            )
        }),
    )
    
    
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'nome',
        'categoria',
        'status',
        'usuario_registro',
        'dono',
        'local',
        'data_registro',
        'data_devolucao',
        'ativo',
    )

    list_display_links = ('id', 'nome',)

    list_filter = (
        'status',
        'categoria',
        'local',
        'ativo',
        'data_registro',
    )

    search_fields = (
        'nome',
        'descricao',
        'codigo',
        'marca_ou_modelo',
        'usuario_registro__username',
        'dono__username',
    )

    list_editable = ('status', 'ativo',)

    fieldsets = (
        ('Informações gerais', {
            'fields': (
                'uuid',
                'codigo',
                'nome',
                'descricao',
                'foto',
                'status',
                'ativo',
            )
        }),
        ('Detalhes do item', {
            'fields': (
                'categoria',
                'tamanho',
                'cor',
                'material',
                'marca_ou_modelo',
            )
        }),
        ('Registro e usuários', {
            'fields': (
                'usuario_registro',
                'dono',
                'local',
                'data_registro',
                'data_atualizacao',
                'data_devolucao',
            )
        }),
    )

    ordering = ('-data_registro',)

    readonly_fields = ('uuid', 'data_registro', 'data_atualizacao')