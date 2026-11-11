from django.db import models
from django.contrib.auth.models import AbstractUser 

class User(AbstractUser):
    is_psicologo = models.BooleanField(default=False)
    is_paciente = models.BooleanField(default=False)

class Psicologo(models.model):
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='perfil_psicologo') 
    CRP = models.CharField(max_length=20, unique=True)
    especialidade = models.CharField(max_length=20)
