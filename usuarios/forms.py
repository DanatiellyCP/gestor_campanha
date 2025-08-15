# usuarios/forms.py
from django import forms
from campanha.models import Sorteios

class SorteiosForm(forms.ModelForm):
    class Meta:
        model = Sorteios
        fields = [
            'data_sorteio',
            'hora_sorteio',
            'usuario_id',
            'status',
            'observacoes',
            'resultado_sorteio',
        ]
        widgets = {
            'data_sorteio': forms.DateInput(attrs={'type': 'date'}),
            'hora_sorteio': forms.TimeInput(attrs={'type': 'time'}),
        }
