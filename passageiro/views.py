from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario,Passageiro, Corrida, Passageiros_corrida
from django.contrib.auth.decorators import login_required
import googlemaps

@login_required
def initial(request, usuario_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        context = {'usuario': usuario}
        return render(request, 'passageiro/initial.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))

@login_required
def UpdateView(request, usuario_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == "POST":
        usuario.foto = request.FILES.get('foto')
        usuario.username = request.POST['username']
        usuario.first_name = request.POST['first_name']
        usuario.last_name = request.POST['last_name']
        usuario.email = request.POST['email']
        usuario.telefone = request.POST['telefone']
        usuario.RG = request.POST['RG']
        usuario.save()
        return HttpResponseRedirect(
            reverse('passageiro:initial', args=(usuario.id, )))
    if usuario.is_passageiro and usuario.id == user.id:
        context = {'usuario': usuario}
        return render(request, 'passageiro/edit.html', context)
    else :
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))
        
@login_required
def Search_RequestView(request, usuario_id, corrida_id=None):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        passageiro = Passageiro.objects.filter(usuario_id=usuario.id)[0]
        context = {}
        if request.GET.get('query', False):
            search_term = request.GET['query'].lower()
            corrida_list = Corrida.objects.filter(
                dia__icontains=search_term,
                ativa=True,
                vagas__gt=0
                )
            htmlEQ = {
                'True': {'title': 'Corrida solicitada'},
                'False': {'title': 'Solicitar corrida'}
            }
            for c in corrida_list:
                c.exists = Passageiros_corrida.objects.filter(
                passageiro=passageiro, corrida=c
                ).exists()
                c.title = htmlEQ[str(c.exists)]['title']
            context = {"corrida_list": corrida_list}
        if corrida_id:
            corrida = get_object_or_404(Corrida, pk=corrida_id)
            passageiro_corrida = Passageiros_corrida(passageiro = passageiro, corrida = corrida)
            passageiro_corrida.save()
                
        return render(request, 'passageiro/search.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))
        
@login_required
def ListView(request, usuario_id, aceito):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        passageiro = Passageiro.objects.filter(usuario_id=usuario.id)[0]
        strToBool = {'accepted': True, 'requested': None, 'rejected': False}
        title = {'accepted': 'aceitas', 'requested': 'solicitadas', 'rejected': 'rejeitadas'}
        list = Passageiros_corrida.objects.filter(
            passageiro_id=passageiro.id,
            aceito=strToBool[aceito])
        corrida_list = []
        for c in list:
            corrida = Corrida.objects.filter(id=c.corrida_id)[0]
            corrida_list.append(corrida)
        context = {"corrida_list": corrida_list, "title": title[aceito]}
        return render(request, 'passageiro/list.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))