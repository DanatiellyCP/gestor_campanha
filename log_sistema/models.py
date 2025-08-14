from django.db import models
from participantes.models import Participantes
from usuarios.models import Usuarios

# Create your models here.

class Log_participante(models.Model):
    data = models.DateField(auto_now_add=True),
    hora =  models.TimeField(auto_now_add=True),
    participante_id = models.ForeignKey(Participantes, on_delete=models.CASCADE),
    tabela = models.CharField(max_length=255),
    dados = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"log - {self.id} - {self.data} - {self.participante_id}"


class Log_usuarios(models.Model):
    data = models.DateField(auto_now_add=True),
    hora =  models.TimeField(auto_now_add=True),
    usuario_id = models.ForeignKey(Participantes, on_delete=models.CASCADE),
    tabela = models.CharField(max_length=255),
    dados = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"log - {self.id} - {self.data} - {self.usuario_id}"