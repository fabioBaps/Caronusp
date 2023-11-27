from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario, Passageiro, Corrida, Passageiros_corrida, Carona
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
        # usuario.foto = request.POST['foto']
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
        strToBool = {'accepted': True, 'requested': None, 'rejected': False, 'ended': True}
        title = {'accepted': 'aceitas', 'requested': 'solicitadas', 'rejected': 'rejeitadas', 'ended': 'finalizadas'}
        list = Passageiros_corrida.objects.filter(
            passageiro_id=passageiro.id,
            aceito=strToBool[aceito])
        corrida_list = []
        for c in list:
            ativa = True
            if aceito == 'ended':
                ativa = False
            corrida = Corrida.objects.filter(id=c.corrida_id, ativa=ativa)
            if corrida:
                corrida_list.append(corrida[0])
        context = {"corrida_list": corrida_list, "title": title[aceito]}
        return render(request, 'passageiro/list.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))
        
@login_required
def DetailView(request, usuario_id, corrida_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        passageiro = Passageiro.objects.filter(usuario_id=usuario.id)[0]
        corrida = get_object_or_404(Corrida, pk=corrida_id)
        carona = Carona.objects.filter(id=corrida.carona_id)[0]
        passageiros = Passageiros_corrida.objects.filter(corrida=corrida, aceito=True)
        ids_passageiros = passageiros.values_list('passageiro_id', flat=True)
        corrida.contains = passageiro.id in ids_passageiros
        context = {"corrida": corrida, "carona": carona}
        return render(request, 'passageiro/race_detail.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))
        
@login_required
def LeaveView(request, usuario_id, corrida_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        passageiro = Passageiro.objects.filter(usuario_id=usuario.id)[0]
        corrida = get_object_or_404(Corrida, pk=corrida_id)
        passageiro_corrida = Passageiros_corrida.objects.filter(passageiro=passageiro, corrida=corrida, aceito=True)
        if passageiro_corrida and corrida.ativa:
            if request.method == "POST":
                passageiro_corrida[0].delete()
                corrida.vagas += 1
                corrida.save()
                return HttpResponseRedirect(
                    reverse('passageiro:detail', args=(usuario.id, corrida.id, )))
            else:
                return render(request, 'passageiro/leave_race.html', {'usuario': usuario, 'corrida': corrida})
        else:
            return HttpResponseRedirect(
                reverse('passageiro:detail', args=(usuario.id, corrida.id, )))
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))