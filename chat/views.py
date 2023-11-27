from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario, Condutor, Carona, Corrida, Passageiros_corrida, Passageiro, Mensagem
from django.contrib.auth.decorators import login_required
from .forms import MensagemForm

@login_required
def chat_corrida(request, corrida_id):
    corrida = get_object_or_404(Corrida, id=corrida_id)
    mensagens = Mensagem.objects.filter(corrida=corrida)
    
    if request.method == 'POST':
        form = MensagemForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.usuario = request.user
            mensagem.corrida = corrida
            mensagem.save()
            return render(request, 'chat/chat_corrida.html', {'corrida_id': corrida_id, 'form': form, 'mensagens': mensagens})
    else:
        form = MensagemForm()

    return render(request, 'chat/chat_corrida.html', {'corrida_id': corrida_id, 'form': form, 'mensagens': mensagens})
