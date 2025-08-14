from django.db import models
from usuarios.models import Usuarios

# models para o APP campanha, para as configurações da campanha pelos usuários responsáveis - Danny - 13-08-2025

class Faq(models.Model):
    data = models.DateField(blank=True, null=True)
    hora =  models.TimeField(blank=True, null=True)
    usuario_id = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    pergunta = models.TextField(blank=True, null=True)
    resposta = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Pergunta  {self.pergunta} - Resposta {self.resposta}"


class Soteios(models.Model):
    data_cadastro = models.DateField(blank=True, null=True)
    hora_cadastro =  models.TimeField(blank=True, null=True)
    usuario_id = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    data_sorteio = models.DateField(blank=True, null=True)
    hora_sorteio =  models.TimeField(blank=True, null=True)

    STATUS = [
        ('1', 'Aberto'),
        ('2', 'Finalizado'),
        
    ]
    status = models.CharField(max_length=1, choices=STATUS, blank=True, null=True)

    observacoes = models.TextField(blank=True, null=True),
    resultado_sorteio = models.CharField(max_length=200)
    def __str__(self):
        return f"log - {self.data_sorteio} - {self.hora_sorteio} - {self.status}"

class Regras(models.Model):
    max_data_cupom_aceito = models.DateField(blank=True, null=True)
    min_data_cupom_aceito = models.DateField(blank=True, null=True)
    qtd_cupom_dia = models.IntegerField(blank=True, null=True)
