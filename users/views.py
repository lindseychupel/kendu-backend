
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from .models import Psicologo, Paciente
from .serializers import PsicologoSerializer, PacienteSerializer



class PsicologoCreateView(CreateAPIView):

    queryset = Psicologo.objects.all()
    serializer_class = PsicologoSerializer
    permission_classes = [AllowAny]


class PacienteCreateView(CreateAPIView):

    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [AllowAny]