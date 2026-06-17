import random
from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import AbstractUser
import unicodedata
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .utils import gerar_codigo_aleatorio
import uuid

# Create your models here.


class Local(models.Model):
    codigo = models.CharField(
        "Código do local",
        unique=True,
        max_length=10,
        blank=True
    )
    predio = models.CharField("Prédio", max_length=5)
    andar = models.CharField("Andar", max_length=5)
    nome = models.CharField("Nome do local", max_length=25, default="Sala do IFPI")
    telefone = models.CharField("Telefone do local", max_length=15, blank=True, null=True)
    descricao = models.TextField("Descrição do local", blank=True, null=True)
    sala_de_aula = models.BooleanField("Sala de aula?", default=False)
    laboratorio = models.BooleanField("Laboratório?", default=False)
    ativa = models.BooleanField("Ativo", default=True)

    def __str__(self):
        return f"{self.nome} - Prédio {self.predio}, Andar {self.andar}"

    class Meta:
        verbose_name = "Local"
        verbose_name_plural = "Locais"

    def gerar_codigo(self):
        nome_normalizado = unicodedata.normalize("NFKD", self.nome or "")
        nome_sem_acento = "".join(
            letra for letra in nome_normalizado
            if not unicodedata.combining(letra)
        )

        letras = "".join(
            letra for letra in nome_sem_acento.upper()
            if letra.isalpha()
        )

        prefixo = letras[:3].ljust(3, "X")

        locais = type(self).objects.exclude(pk=self.pk)

        for numero in range(100):
            codigo = f"{prefixo}{numero:03d}"

            if not locais.filter(codigo=codigo).exists():
                return codigo

        raise ValidationError(
            f"Não há códigos disponíveis para o prefixo '{prefixo}'."
        )

    def save(self, *args, **kwargs):
        if not self.nome:
            raise ValidationError({
                "nome": "O nome do local é obrigatório."
            })

        codigo_foi_gerado = not self.codigo

        if codigo_foi_gerado:
            self.codigo = self.gerar_codigo()

        for tentativa in range(3):
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)

            except IntegrityError:
                if self.pk or tentativa == 2:
                    raise

                if codigo_foi_gerado:
                    self.codigo = self.gerar_codigo()


class Usuario(AbstractUser):
    
    TIPO = [
        (1, "Usuário"),
        (2, "Servidor"),

]
    
    username = models.CharField(max_length=100, unique=True)
    nome = models.CharField("Nome", max_length=100, blank=True, null=True)
    email = models.EmailField("Email", max_length=100, unique=True)
    telefone = models.CharField("Telefone", max_length=15, blank=True, null=True)
    data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)
    cpf = models.CharField("CPF", max_length=14, unique=True, blank=True, null=True)
    foto = models.ImageField("Foto de Perfil", upload_to="usuarios/fotos/", blank=True, null=True)
    tipo = models.PositiveSmallIntegerField("Tipo de Usuário", choices=TIPO, blank=True, null=True)
    matricula = models.CharField("Matrícula", max_length=20, blank=True, null=True, help_text="Apenas para alunos.")
    setor = models.CharField("Setor", max_length=100, blank=True, null=True, help_text="Apenas para servidores.")
    criado_em = models.DateField(auto_now=True)
    ativo = models.BooleanField("Ativo", default=True)
    local = models.ForeignKey(Local, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Local de cadastro")
    senha_alterada = models.BooleanField("Senha alterada?", default=False)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def gerar_username(self):
        email = self.email or "usuario"

        if "@" in email:
            base_username = email.split("@")[0]
        else:
            base_username = email

        while True:
            numeros_aleatorios = "".join(random.choices("0123456789", k=4))
            username = f"{base_username}{numeros_aleatorios}"

            if not Usuario.objects.filter(username=username).exists():
                break

        return username

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]
        elif self.email:
            return self.email.split("@")[0]
        else:
            return self.username
            
    
    def gerar_senha_padrao(self):
        if self.cpf:
            return self.cpf.replace(".", "").replace("-", "")
        return None
    

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.gerar_username()
            
        if not self.password:
            senha_padrao = self.gerar_senha_padrao()
            if senha_padrao:
                self.set_password(senha_padrao)            
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Categoria(models.Model):
    codigo = models.CharField(
        "Código da categoria",
        unique=True,
        max_length=10,
        blank=True
    )
    nome = models.CharField("Nome da categoria", max_length=25)
    descricao = models.TextField("Descrição da categoria", blank=True, null=True)
    ativa = models.BooleanField("Ativo", default=True)
    slug = models.SlugField(
        "Slug",
        unique=True,
        max_length=60,
        blank=True
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "categorias"

    def gerar_codigo(self):
        nome_normalizado = unicodedata.normalize("NFKD", self.nome or "")
        nome_sem_acento = "".join(
            letra for letra in nome_normalizado
            if not unicodedata.combining(letra)
        )

        letras = "".join(
            letra for letra in nome_sem_acento.upper()
            if letra.isalpha()
        )

        prefixo = letras[:3].ljust(3, "X")

        categorias = type(self).objects.exclude(pk=self.pk)

        for numero in range(100):
            codigo = f"{prefixo}{numero:02d}"

            if not categorias.filter(codigo=codigo).exists():
                return codigo

        raise ValidationError(
            f"Não há códigos disponíveis para o prefixo '{prefixo}'."
        )

    def gerar_slug_unico(self):
        max_length = self._meta.get_field("slug").max_length

        slug_base = slugify(self.nome or "")

        if not slug_base:
            slug_base = "categoria"

        slug_base = slug_base[:max_length].strip("-")

        categorias = type(self).objects.exclude(pk=self.pk)

        slug = slug_base
        contador = 2

        while categorias.filter(slug=slug).exists():
            sufixo = f"-{contador}"
            tamanho_base = max_length - len(sufixo)

            slug = f"{slug_base[:tamanho_base].rstrip('-')}{sufixo}"
            contador += 1

        return slug

    def save(self, *args, **kwargs):
        if not self.nome:
            raise ValidationError({
                "nome": "O nome da categoria é obrigatório."
            })

        codigo_foi_gerado = not self.codigo
        slug_foi_gerado = not self.slug

        if codigo_foi_gerado:
            self.codigo = self.gerar_codigo()

        if slug_foi_gerado:
            self.slug = self.gerar_slug_unico()

        for tentativa in range(3):
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)

            except IntegrityError:
                if self.pk or tentativa == 2:
                    raise

                if codigo_foi_gerado:
                    self.codigo = self.gerar_codigo()

                if slug_foi_gerado:
                    self.slug = self.gerar_slug_unico()


class Atividade(models.Model):
    CORES = [
        ("primary", "Azul"),
        ("success", "Verde"),
        ("warning", "Amarelo"),
        ("danger", "Vermelho"),
        ("info", "Azul claro"),
        ("secondary", "Cinza"),
    ]

    
    titulo = models.CharField("Título", max_length=100)
    descricao = models.CharField("Descrição", max_length=255)
    cor = models.CharField("Cor", max_length=20, choices=CORES, default="primary")
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"
        ordering = ["-criado_em"]
        
class Item(models.Model):
    
    STATUS = [
        (1, "Perdido"),
        (2, "Encontrado"),
        (3, "Devolvido"),
        (4, "Outro"),
    ]
    
    uuid = models.CharField("UUID", max_length=36, unique=True, blank=True)
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.SET_NULL, related_name='usuario_registro', verbose_name="Usuário responsável", blank=True, null=True)
    dono = models.ForeignKey(Usuario, on_delete=models.SET_NULL, blank=True, null=True, related_name='itens_recuperados', verbose_name="Dono do item")
    tamanho = models.CharField("Tamanho do item", max_length=20, blank=True, null=True)
    cor = models.CharField("Cor do item", max_length=20, blank=True, null=True)
    material = models.CharField("Material do item", max_length=50, blank=True, null=True)   
    codigo = models.CharField("Código do item", max_length=10, unique=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Categoria")
    marca_ou_modelo = models.CharField("Marca ou modelo do item", max_length=50, blank=True, null=True)
    nome = models.CharField("Nome do item", max_length=100, blank=True, null=True)
    local = models.ForeignKey(Local, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Local que foi encontrado")
    local_guardado = models.ForeignKey(Local, on_delete=models.SET_NULL, blank=True, null=True, related_name="itens_guardados", verbose_name="Local guardado" )
    data_registro = models.DateTimeField("Data de registro", auto_now_add=True)
    data_devolucao = models.DateTimeField("Data de devolução", blank=True, null=True)
    data_atualizacao = models.DateTimeField("Data de atualização", auto_now=True)
    ativo = models.BooleanField("Ativo", default=True)
    foto = models.ImageField("Foto do item", upload_to="itens/fotos/", blank=True, null=True)
    descricao = models.TextField("Descrição do item", blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)
    status = models.IntegerField("Status", choices=STATUS, default=1)

    def __str__(self):
        return self.categoria.nome if self.categoria else f"Item {self.id}"

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        
        

    def save(self, *args, **kwargs):
        # Gera UUID se não tiver
        if not self.uuid:
            self.uuid = str(uuid.uuid4())

        # Gerar código automaticamente se estiver em branco
        if not self.codigo:
            codigo = gerar_codigo_aleatorio()
            while Item.objects.filter(codigo=codigo).exists():
                codigo = gerar_codigo_aleatorio()
            self.codigo = codigo

        super().save(*args, **kwargs)