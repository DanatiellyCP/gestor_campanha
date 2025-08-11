from django.db import models

class Serie(models.Model):
    nome_serie = models.CharField(max_length=50)  # serie_00 ~ serie_99
    numero_atual = models.PositiveIntegerField(default=0)  # 0 ~ 99.999
    status = models.CharField(max_length=50, default='Aberto')  # depois de 100 passar para fechado

    def __str__(self):
        return str(self.numero_atual)


