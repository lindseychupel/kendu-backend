from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_psicologo = models.BooleanField(default=False)
    is_paciente = models.BooleanField(default=False)


class Psicologo(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_psicologo'
    )

    crp = models.CharField(max_length=20, unique=True)
    especialidade = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

class Paciente(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_paciente'
    )

    Psicologo = models.ForeignKey(
        
    )
