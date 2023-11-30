from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario, Condutor, Passageiro, Corrida, Passageiros_corrida, Carona, Avaliacao_Condutor, Notificacao
from django.contrib.auth.decorators import login_required
import googlemaps
import requests
from datetime import datetime, timedelta
import numpy as np
import os
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

@login_required
def initial(request, usuario_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        notificacoes = Notificacao.objects.filter(usuario=usuario, para_condutor=False, visto=False)
        context = {'usuario': usuario, 'notificacoes':notificacoes}
        return render(request, 'passageiro/initial.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))

@login_required
def UpdateView(request, usuario_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == "POST":
        if request.FILES.get('foto'):
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
        if request.method == 'POST' and request.POST.get('horario_chegada'):
            api_key = GOOGLE_API_KEY
            chegada = request.POST.get('local_chegada')
            chegada_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={chegada}&key={api_key}"
            chegada_response = requests.get(chegada_url)
            chegada_data = chegada_response.json()
            chegada_result = chegada_data.get('results', [])
            if chegada_result:
                top_chegada = chegada_result[0]
                id_chegada = top_chegada['formatted_address']

            partida = request.POST.get('local_partida')
            partida_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={partida}&key={api_key}"
            partida_response = requests.get(partida_url)
            partida_data = partida_response.json()
            partida_result = partida_data.get('results', [])
            if partida_result:
                top_partida = partida_result[0]
                id_partida = top_partida['formatted_address']

            input_time_str = request.POST.get('horario_chegada')
            input_time = datetime.strptime(input_time_str, '%H:%M').time()
            thirty_minutes_before = (datetime.combine(datetime.today(), input_time) - timedelta(minutes=30)).time()

            caronas = Carona.objects.filter(horario_chegada__lte=input_time, horario_chegada__gte=thirty_minutes_before)
            if len(caronas) == 0: return HttpResponseRedirect(reverse('passageiro:search', args=(user.id, )))
                                                                

            chegadas_ids = [carona.endereco_chegada for carona in caronas]
            print(chegadas_ids)

            gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

            chegadas_dm = gmaps.distance_matrix(id_chegada, chegadas_ids, units='metric')

            if 'rows' in chegadas_dm and 'elements' in chegadas_dm['rows'][0]:
                chegadas_dict = {}
                elements = chegadas_dm['rows'][0]['elements']
                for i, carona in enumerate(caronas):
                    distance = elements[i].get('distance', {})
                    # Convert the distance from meters to kilometers
                    distance_num = distance.get('value', float('inf')) / 1000
                    chegadas_dict[carona] = distance_num
                
                caronas = [carona for carona in caronas if chegadas_dict[carona]<=5]
            
            if len(caronas) == 0: return HttpResponseRedirect(reverse('passageiro:search', args=(user.id, )))
            
            partidas_ids = [carona.endereco_partida for carona in caronas]
            partidas_dm = gmaps.distance_matrix(id_partida, partidas_ids, units='metric')

            if 'rows' in partidas_dm and 'elements' in partidas_dm['rows'][0]:
                partidas_dict = {}
                elements = partidas_dm['rows'][0]['elements']
                for i, carona in enumerate(caronas):
                    distance = elements[i].get('distance', {})
                    # Convert the distance from meters to kilometers
                    distance_num = distance.get('value', float('inf')) / 1000
                    partidas_dict[carona] = distance_num
                
                caronas = [carona for carona in caronas if partidas_dict[carona]<=5]
            if len(caronas) == 0: return HttpResponseRedirect(reverse('passageiro:search', args=(user.id, )))


            dia = request.POST['dia'].lower()
            corrida_list = Corrida.objects.filter(
                dia=dia,
                ativa=True,
                vagas__gt=0,
                carona__in = caronas
                )
            corrida_list = [item for item in corrida_list if item.carona.condutor.usuario.id != usuario_id]
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

            texto_notificação = f'{passageiro.usuario.first_name} {passageiro.usuario.last_name} solicitou entrada na sua corrida de {corrida.dia}. Responda sua solicitação!'
            notificacao = Notificacao(usuario=corrida.carona.condutor.usuario, texto=texto_notificação, para_condutor=True)
            notificacao.save()
                
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
            c.ativa = True
            if aceito == 'ended':
                c.ativa = False
            corrida = Corrida.objects.filter(id=c.corrida_id, ativa=c.ativa)
            if corrida:
                corrida[0].aval = Avaliacao_Condutor.objects.filter(avaliador_id = passageiro.id, corrida_id = corrida[0].id)
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
        
@login_required
def AvaliacaoView(request, usuario_id, corrida_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        passageiro = Passageiro.objects.filter(usuario_id=usuario.id)[0]
        corrida = get_object_or_404(Corrida, pk=corrida_id)
        carona = get_object_or_404(Carona, pk=corrida.carona_id)
        condutor = get_object_or_404(Condutor, pk=carona.condutor_id)
        corrida.condutor = condutor
        passageiro_corrida = Passageiros_corrida.objects.filter(passageiro=passageiro, corrida=corrida, aceito=True)
        if passageiro_corrida and (not corrida.ativa):
            if request.method == "POST":
                avaliacao = Avaliacao_Condutor(avaliador=passageiro, avaliado=condutor, corrida=corrida, nota=request.POST['nota'])
                avaliacao.save()
                recalcula_media_condutor(condutor.id)
                return HttpResponseRedirect(
                    reverse('passageiro:list-ended', args=(usuario.id, 'ended', )))
            else:
                return render(request, 'passageiro/rate.html', {'corrida': corrida})
        else:
            return HttpResponseRedirect(
                reverse('passageiro:list-ended', args=(usuario.id, 'ended', )))
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))
        
def recalcula_media_condutor(condutor_id):
    condutor = get_object_or_404(Condutor, pk=condutor_id)
    avaliacoes = Avaliacao_Condutor.objects.filter(avaliado=condutor.id)
    nota_media = np.mean([item.nota for item in avaliacoes ])
    condutor.nota_media = nota_media
    condutor.save()


def read_notificacao(request, usuario_id, notificacao_id):
    notificacao = get_object_or_404(Notificacao,pk=notificacao_id)
    notificacao.visto = True
    notificacao.save()
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_passageiro and usuario.id == user.id:
        notificacoes = Notificacao.objects.filter(usuario=usuario, para_condutor=False, visto=False)
        context = {'usuario': usuario, 'notificacoes':notificacoes}
        return render(request, 'passageiro/initial.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))
        
@login_required
def condutordetail(request, usuario_id, condutor_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    condutor = get_object_or_404(Condutor, pk=condutor_id)
    if usuario.is_passageiro and usuario.id == user.id:
        context = {'usuario': usuario, 'condutor': condutor}
        return render(request, 'passageiro/detail_condutor.html', context)
    else:
        return HttpResponseRedirect(
            reverse('accounts:afterlogin', args=(user.id, )))