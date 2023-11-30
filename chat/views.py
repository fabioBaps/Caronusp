from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario, Condutor, Carona, Corrida, Passageiros_corrida, Passageiro, Mensagem, Notificacao
from django.contrib.auth.decorators import login_required
from .forms import MensagemForm


def checa_login(request, usuario_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.id == user.id:
        return True
    return False


@login_required
def chat_corrida(request, usuario_id, corrida_id, type_actor):
    # type_actor =  1:passageiro, 0:condutor
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    corrida = get_object_or_404(Corrida, id=corrida_id)
    passageiros_da_corrida = Passageiros_corrida.objects.filter(corrida=corrida,aceito=True)

    if not type_actor in [0,1]: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    if type_actor == 0:
        if not corrida.carona.condutor.usuario.id == request.user.id:
            return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    if type_actor == 1:
        if not usuario.is_passageiro: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
        passageiro = get_object_or_404(Passageiro, usuario=usuario)
        if passageiro not in [item.passageiro for item in passageiros_da_corrida]: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))

    mensagens = Mensagem.objects.filter(corrida=corrida)
    if request.method == 'POST':
        form = MensagemForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.usuario = request.user
            mensagem.corrida = corrida
            mensagem.save()

            outros_passageiros = [item for item in passageiros_da_corrida if item.passageiro.usuario.id != usuario_id]
            for passageiro in outros_passageiros:
                texto_notificação = f'{usuario.first_name} {usuario.last_name} enviou uma mensagem no chat da corrida do dia {corrida.dia}: "{mensagem.texto}"'
                notificacao = Notificacao(usuario=passageiro.passageiro.usuario, texto=texto_notificação, para_condutor=False)
                notificacao.save()
            if type_actor == 1:
                texto_notificação = f'{usuario.first_name} {usuario.last_name} enviou uma mensagem no chat da sua corrida do dia {corrida.dia}: "{mensagem.texto}"'
                notificacao = Notificacao(usuario=corrida.carona.condutor.usuario, texto=texto_notificação, para_condutor=True)
                notificacao.save()

            form = MensagemForm()
            return render(request, 'chat/chat_corrida.html', {'corrida_id': corrida_id,'corrida': corrida, 'form': form, 'mensagens': mensagens, 'type_actor':type_actor})

    form = MensagemForm()
    return render(request, 'chat/chat_corrida.html', {'corrida_id': corrida_id,'corrida': corrida, 'form': form, 'mensagens': mensagens,'type_actor':type_actor})
