from django.db import models

# Create your models here.
class Participantes(models.Model):
  nome = models.CharField(max_length=255)
  dt_nasc = models.DateField(blank=True, editable=True, null=True)
  cpf = models.CharField(max_length=20)
  #telefone = models.CharField(max_length=20)
  celular = models.CharField(max_length=20)
  email = models.CharField(max_length=255)
  uf = models.CharField(max_length=40)
  cidade = models.CharField(max_length=100)
  cep = models.CharField(max_length=100)
  rua = models.CharField(max_length=100)
  bairro = models.CharField(max_length=100)
  num = models.IntegerField(blank=True, editable=True, null=True)
  senha = models.CharField(max_length=128)  # Ideal para senhas criptografadas
  aceita_termos = models.BooleanField(default=False)
  aceita_msg_whatsapp = models.BooleanField(default=False)
  aceita_info_bombril = models.BooleanField(default=False)
  data_cadastro = models.DateTimeField(auto_now_add=True)

  # Status do participante
  STATUS = [
        ('1', 'Ativo'),
        ('2', 'Inativo')
    ]
  status = models.CharField(max_length=1, choices=STATUS, default='1')

  # novos campos solicitados
  complemento = models.CharField(max_length=100, blank=True, editable=True, null=True)

  CADASTRO = [
        ('1', 'Whatsapp'),
        ('2', 'Hotsite')
    ]
  cadastro = models.CharField(max_length=1, choices=CADASTRO, default='2') 
  data_cadastro = models.DateField(auto_now_add=True)

