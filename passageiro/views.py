from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario,Passageiro, Corrida, Passageiros_corrida, Carona
from django.contrib.auth.decorators import login_required
import googlemaps
from _env import GOOGLE_API_KEY
import requests
from datetime import datetime, timedelta

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
        if request.method == 'POST':
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
                dia__icontains=dia,
                ativa=True,
                vagas__gt=0,
                carona__in = caronas
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