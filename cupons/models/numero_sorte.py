from django.db import models
from .cupom import Cupom
from participantes.models import Participantes

class NumeroDaSorte(models.Model):
    cupom = models.ForeignKey(Cupom, on_delete=models.CASCADE)
    participante = models.ForeignKey(Participantes, on_delete=models.CASCADE)
    numero = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='ativo')

    def __str__(self):
        return self.numero


