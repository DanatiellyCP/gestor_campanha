from django.contrib import admin
from .models import Participantes

# Register your models here.
class ParticipantesAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'celular', 'email', 'dt_nasc', 'uf', 'cidade', 'cep', 'rua', 'bairro', 'num', 'senha')
    list_filter = ('uf', 'cidade')
    search_fields = ('nome', 'cpf', 'celular', 'email')
    ordering = ('-id',)

admin.site.register(Participantes, ParticipantesAdmin)
