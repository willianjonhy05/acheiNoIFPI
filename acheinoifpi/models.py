from django.shortcuts import render
import random
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Usuario(AbstractUser):
    
    TIPO = [
        (1, "Aluno"),
        (2, "Servidor"),

]
    
    username = models.CharField(max_length=100, unique=True)
    nome = models.CharField("Nome", max_length=100, blank=True, null=True)
    email = models.EmailField("Email", max_length=100, unique=True)
    data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)
    cpf = models.CharField("CPF", max_length=14, blank=True, null=True)
    foto = models.ImageField("Foto de Perfil", upload_to="usuarios/fotos/", blank=True, null=True)
    tipo = models.PositiveSmallIntegerField("Tipo de Usuário", choices=TIPO)
    matricula = models.CharField("Matrícula", max_length=20, blank=True, null=True, help_text="Apenas para alunos.")
    setor = models.CharField("Setor", max_length=100, blank=True, null=True, help_text="Apenas para servidores.")
    

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

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.gerar_username()
            

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"