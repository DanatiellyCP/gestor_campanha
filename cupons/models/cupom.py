from django.db import models
from participantes.models import Participantes

class Cupom(models.Model):
    participante = models.ForeignKey(Participantes, on_delete=models.CASCADE)
    nome_loja = models.CharField(max_length=255)
    cnpj_loja = models.CharField(max_length=20)
    tipo_documento = models.CharField(max_length=50)
    numero_documento = models.CharField(max_length=100, unique=True)
    imagem_cupom = models.ImageField(upload_to='cupons/', blank=True, null=True)
    #models.ImageField(upload_to='foto_cupom/', blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_cadastro = models.DateField(auto_now_add=True)
    hora_cadastro = models.TimeField(auto_now_add=True)
    dados_cupom = models.TextField(blank=True, null=True)
    ocr_text = models.TextField(blank=True, null=True, verbose_name="Texto OCR bruto")
    link_consulta = models.URLField(blank=True, null=True)
    dados_json = models.JSONField(default=dict,blank=True, null=True)

    
    TIPO_ENVIO = [
        ('1', 'whatsapp'),
        ('2', 'hotsite')
    ]
    
    tipo_envio = models.CharField(max_length=50)
    
     # Status do participante
    STATUS = [
        ('Pendente', 'Pendente'),
        ('Validado', 'Validado'),
        ('Invalidado', 'Invalidado')
    ]
    
    status = models.CharField(max_length=50, default='Pendente')

    def __str__(self):
        return f"Cupom {self.id} - {self.nome_loja}"
