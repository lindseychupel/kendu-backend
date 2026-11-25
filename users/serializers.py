

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password

from .models import (
    User,
    Psicologo,
    Paciente,
    ConvitePaciente,
    SolicitacaoConexao
)


# CADASTRO DO PSICÓLOGO

class PsicologoSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    password = serializers.CharField(
        source='user.password',
        write_only=True,
        trim_whitespace=False
    )

    class Meta:
        model = Psicologo
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'crp',
            'especialidade',
            'biografia',
            'formacao',
            'abordagem_terapeutica',
            'experiencia',
            'foto_perfil',
            'perfil_publico',
        ]

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):

        user_data = validated_data.pop('user')

        user = User.objects.create_user(
            **user_data,
            is_psicologo=True
        )

        psicologo = Psicologo.objects.create(
            user=user,
            **validated_data
        )

        return psicologo


# CADASTRO INDEPENDENTE DO PACIENTE

class PacienteSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    password = serializers.CharField(
        source='user.password',
        write_only=True,
        trim_whitespace=False
    )

    class Meta:
        model = Paciente
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):

        user_data = validated_data.pop('user')

        user = User.objects.create_user(
            **user_data,
            is_paciente=True
        )

        paciente = Paciente.objects.create(
            user=user
        )

        return paciente


# CRIAÇÃO DE CONVITE PELO PSICÓLOGO

class ConvitePacienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConvitePaciente
        fields = [
            'nome',
            'sobrenome',
            'email',
        ]

    def validate_email(self, value):

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Já existe um usuário cadastrado com este e-mail.'
            )

        return value


# FINALIZAÇÃO DO CADASTRO POR CONVITE

class FinalizarCadastroPacienteSerializer(serializers.Serializer):

    token = serializers.UUIDField()

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False
    )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):

        try:
            convite = ConvitePaciente.objects.select_related(
                'psicologo'
            ).get(token=attrs['token'])

        except ConvitePaciente.DoesNotExist:
            raise serializers.ValidationError(
                'Convite não encontrado.'
            )

        if convite.status != ConvitePaciente.Status.PENDENTE:
            raise serializers.ValidationError(
                'Este convite não está mais disponível.'
            )

        if convite.expira_em and convite.expira_em <= timezone.now():
            raise serializers.ValidationError(
                'Este convite expirou.'
            )

        if User.objects.filter(email__iexact=convite.email).exists():
            raise serializers.ValidationError(
                'Já existe uma conta cadastrada com este e-mail.'
            )

        attrs['convite'] = convite

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        convite = validated_data['convite']

        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=convite.nome,
            last_name=convite.sobrenome,
            email=convite.email,
            password=validated_data['password'],
            is_paciente=True
        )

        paciente = Paciente.objects.create(
            user=user,
            psicologo=convite.psicologo
        )

        convite.status = ConvitePaciente.Status.ACEITO
        convite.aceito_em = timezone.now()
        convite.save(update_fields=['status', 'aceito_em'])

        return paciente


# SOLICITAÇÃO DE CONEXÃO

class SolicitacaoConexaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SolicitacaoConexao
        fields = [
            'psicologo',
            'status',
            'criado_em',
        ]

        read_only_fields = [
            'status',
            'criado_em',
        ]

    def validate_psicologo(self, value):

        if not value.perfil_publico:
            raise serializers.ValidationError(
                'Este psicólogo não possui perfil público.'
            )

        return value

    def validate(self, attrs):

        request = self.context.get('request')

        if request and hasattr(request.user, 'perfil_paciente'):

            paciente = request.user.perfil_paciente
            psicologo = attrs['psicologo']

            if paciente.psicologo_id == psicologo.id:
                raise serializers.ValidationError(
                    'Você já possui vínculo com este psicólogo.'
                )

            solicitacao_existente = SolicitacaoConexao.objects.filter(
                paciente=paciente,
                psicologo=psicologo,
                status=SolicitacaoConexao.Status.PENDENTE
            ).exists()

            if solicitacao_existente:
                raise serializers.ValidationError(
                    'Você já possui uma solicitação pendente para este psicólogo.'
                )

        return attrs
