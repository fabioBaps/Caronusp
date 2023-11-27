from accounts.models import Mensagem
from django import forms

class MensagemForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ['texto']
