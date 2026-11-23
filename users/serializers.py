
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from .models import User, Psicologo, Paciente


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

    psicologo = serializers.PrimaryKeyRelatedField(
        queryset=Psicologo.objects.all()
    )

    class Meta:
        model = Paciente
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'psicologo',
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
            user=user,
            **validated_data
        )

        return paciente
