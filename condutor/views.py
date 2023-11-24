from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario, Condutor, Carona, Corrida
from django.contrib.auth.decorators import login_required
import pandas as pd


@login_required
def initial(request, usuario_id):
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    caronas = Carona.objects.filter(condutor=condutor)
    context = {'usuario_id': usuario_id, 'caronas':caronas}
    return render(request, 'condutor/initial.html', context)

@login_required
def create_carona(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    if request.method == "POST":
        carona_dict = {}
        carona_dict['condutor'] = condutor
        carona_dict['local_chegada'] = request.POST['local_chegada']
        carona_dict['local_partida'] = request.POST['local_partida']
        carona_dict['horario_chegada'] = request.POST['horario_chegada']
        carona_dict['horario_partida'] = request.POST['horario_partida']
        carona_dict['lugares'] = request.POST['vagas']
        carona_dict['placa_veiculo'] = request.POST['placa']
        carona = Carona(**carona_dict)
        carona.save()

        for i in range(1,1+int(request.POST['num_corridas'])):
            print(request.POST.keys())
            corrida_dict = {}
            corrida_dict['carona'] = carona
            corrida_dict['dia'] = request.POST[f'day_{i}']
            if pd.Timestamp(corrida_dict['dia']).date() < pd.to_datetime('today').date():
                corrida_dict['ativa'] = False
            else:
                corrida_dict['ativa'] = True
            corrida_dict['vagas'] = carona_dict['lugares']
            corrida = Corrida(**corrida_dict)
            corrida.save() 

        return HttpResponseRedirect(
            reverse('condutor:initial', args=(usuario.id, )))
    context = {'usuario_id': usuario_id}
    return render(request, 'condutor/create_carona.html', context)


def detail_carona(request, usuario_id, carona_id):
    carona = get_object_or_404(Carona, pk=carona_id)
    corridas = Corrida.objects.filter(carona=carona)
    context = {'usuario_id': usuario_id, 'carona':carona,'corridas':corridas}
    return render(request, 'condutor/detail_carona.html', context)


def edit_carona(request, usuario_id, carona_id):
    carona = get_object_or_404(Carona, pk=carona_id)
    if request.method == "POST":
        carona.local_chegada = request.POST['local_chegada']
        carona.local_partida = request.POST['local_partida']
        carona.horario_chegada = request.POST['horario_chegada']
        carona.horario_partida = request.POST['horario_partida']
        carona.placa_veiculo = request.POST['placa']
        carona.save()
        return HttpResponseRedirect(
            reverse('condutor:detail_carona', args=(usuario_id, carona_id )))
    corridas = Corrida.objects.filter(carona=carona)
    context = {'usuario_id': usuario_id, 'carona':carona,'corridas':corridas}
    return render(request, 'condutor/edit_carona.html', context)

