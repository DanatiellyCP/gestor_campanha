from django.db import models

# Create your models here.

class Skus_validos(models.Model):
    nome = models.CharField(max_length=100, blank=True, editable=True, null=True)
    ean = models.CharField(max_length=100, blank=True, editable=True, null=True)
    dun = models.CharField(max_length=100, blank=True, editable=True, null=True)
    categoria = models.CharField(max_length=50, blank=True, editable=True, null=True)
    is_acelerador = models.BooleanField(default=False)  # Novo campo

    def __str__(self):
      return self.nome