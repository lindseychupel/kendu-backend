import uuid

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

    # Identificação profissional
    crp = models.CharField(max_length=20, unique=True)
    especialidade = models.CharField(max_length=100)

    # Perfil profissional público
    biografia = models.TextField(blank=True)
    formacao = models.TextField(blank=True)
    abordagem_terapeutica = models.TextField(blank=True)
    experiencia = models.TextField(blank=True)

    foto_perfil = models.ImageField(
        upload_to='perfis/psicologos/',
        null=True,
        blank=True
    )

    perfil_publico = models.BooleanField(default=False)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()


class Paciente(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_paciente'
    )

    psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.PROTECT,
        related_name='pacientes',
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()


class ConvitePaciente(models.Model):

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        ACEITO = 'aceito', 'Aceito'
        EXPIRADO = 'expirado', 'Expirado'
        CANCELADO = 'cancelado', 'Cancelado'

    psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name='convites_enviados'
    )

    nome = models.CharField(max_length=150)
    sobrenome = models.CharField(max_length=150)
    email = models.EmailField()

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField(null=True, blank=True)
    aceito_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.nome} - {self.email}'


class SolicitacaoConexao(models.Model):

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        ACEITA = 'aceita', 'Aceita'
        RECUSADA = 'recusada', 'Recusada'

    psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name='solicitacoes_recebidas'
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='solicitacoes_enviadas'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.paciente} -> {self.psicologo} ({self.status})'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['psicologo', 'paciente'],
                condition=models.Q(status='pendente'),
                name='unique_solicitacao_pendente'
            )
        ]
