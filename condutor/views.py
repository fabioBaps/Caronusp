from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario, Condutor, Carona, Corrida, Passageiros_corrida, Passageiro, Avaliacao_Passageiro
from django.contrib.auth.decorators import login_required
import googlemaps
import numpy as np


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
            corrida_dict = {}
            corrida_dict['carona'] = carona
            corrida_dict['dia'] = request.POST[f'day_{i}']
            corrida_dict['ativa'] = True
            corrida_dict['vagas'] = carona_dict['lugares']
            corrida = Corrida(**corrida_dict)
            corrida.save() 

        return HttpResponseRedirect(
            reverse('condutor:initial', args=(usuario.id, )))
    context = {'usuario_id': usuario_id}
    return render(request, 'condutor/create_carona.html', context)

def get_passageiros(corrida):
    passageiros_da_corrida = Passageiros_corrida.objects.filter(corrida=corrida)
    passageiros_aceitos = []
    passageiros_a_aceitar = []
    for passageiro in passageiros_da_corrida:
        passageiro_i = get_object_or_404(Passageiro, pk=passageiro.passageiro.id)
        if passageiro.aceito == True:
            passageiros_aceitos.append(passageiro_i)
        elif passageiro.aceito != False:
            passageiros_a_aceitar.append(passageiro_i)
        # else = passageiro rejeitado
    return {
        'corrida':corrida,
        'passageiros_a_aceitar':passageiros_a_aceitar,
        'passageiros_aceitos':passageiros_aceitos
    }

def detail_carona(request, usuario_id, carona_id):
    carona = get_object_or_404(Carona, pk=carona_id)
    corridas = Corrida.objects.filter(carona=carona, ativa=True)
    info_corridas_passageiros = [get_passageiros(corrida) for corrida in corridas]
    context = {'usuario_id': usuario_id, 'carona':carona, 'info_corridas_passageiros':info_corridas_passageiros}
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
    horario_partida_formatado = str(carona.horario_partida).split(':00')[0]
    horario_chegada_formatado = str(carona.horario_chegada).split(':00')[0]
    context = {'usuario_id': usuario_id, 'carona':carona,'corridas':corridas,'horario_partida_formatado':horario_partida_formatado,'horario_chegada_formatado':horario_chegada_formatado}
    return render(request, 'condutor/edit_carona.html', context)

def delete_corrida(request, usuario_id, corrida_id):
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    if request.method == "POST":
        corrida.delete()
        return HttpResponseRedirect(
            reverse('condutor:detail_carona', args=(usuario_id, corrida.carona.id )))
    context = {'corrida':corrida}
    return render(request, 'condutor/delete_corrida.html', context)

def create_corrida(request, usuario_id, carona_id):
    carona = get_object_or_404(Carona, pk=carona_id)
    if request.method == "POST":
            corrida_dict = {}
            corrida_dict['carona'] = carona
            corrida_dict['dia'] = request.POST['dia']
            corrida_dict['ativa'] = True
            corrida_dict['vagas'] = carona.lugares
            corrida = Corrida(**corrida_dict)
            corrida.save() 
            return HttpResponseRedirect(reverse('condutor:detail_carona', args=(usuario_id, corrida.carona.id )))
    context = {'carona':carona}
    return render(request, 'condutor/create_corrida.html', context)
    
def aceitar_passageiro_corrida(request, usuario_id, corrida_id, passageiro_id):
    passageiro_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, passageiro=passageiro_id)[0]
    passageiro_corrida.aceito = True
    passageiro_corrida.save()
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    carona = get_object_or_404(Carona, pk=corrida.carona.id)
    corridas = Corrida.objects.filter(carona=carona, ativa=True)
    info_corridas_passageiros = [get_passageiros(corrida_) for corrida_ in corridas]
    context = {'usuario_id': usuario_id, 'carona':carona, 'info_corridas_passageiros':info_corridas_passageiros}
    return render(request, 'condutor/detail_carona.html', context)

def rejeitar_passageiro_corrida(request, usuario_id, corrida_id, passageiro_id):
    passageiro_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, passageiro=passageiro_id)[0]
    passageiro_corrida.aceito = False
    passageiro_corrida.save()
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    carona = get_object_or_404(Carona, pk=corrida.carona.id)
    corridas = Corrida.objects.filter(carona=carona, ativa=True)
    info_corridas_passageiros = [get_passageiros(corrida_) for corrida_ in corridas]
    context = {'usuario_id': usuario_id, 'carona':carona, 'info_corridas_passageiros':info_corridas_passageiros}
    return render(request, 'condutor/detail_carona.html', context)

def encerrar_corrida(request, usuario_id, corrida_id):
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    corrida.ativa=False
    corrida.save()
    passageiros_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, aceito=True)
    passageiros_corrida_nao_avaliados = []
    for passageiro in passageiros_corrida:
        try:
            get_object_or_404(Avaliacao_Passageiro, corrida=corrida_id, avaliado=passageiro.id)
            passageiros_corrida_nao_avaliados.append(passageiro)
        except:
            pass
    context = {'usuario_id': usuario_id, 'corrida':corrida, 'passageiros_corrida':passageiros_corrida_nao_avaliados}
    return render(request, 'condutor/avalia_passageiros_corrida.html', context)

def avalia_passageiro_individual(request, usuario_id, corrida_id, passageiro_id):
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    passageiro = get_object_or_404(Passageiro, pk=passageiro_id)
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    if request.method == "POST":
        nota = request.POST['nota']
        avaliacao = Avaliacao_Passageiro(corrida=corrida,avaliador=condutor,avaliado=passageiro,nota=nota)
        avaliacao.save()
        recalcula_media_passageiro(passageiro_id)
        return HttpResponseRedirect(
            reverse('condutor:encerrar_corrida', args=(usuario_id, corrida.id )))
    passageiros_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, aceito=True)
    context = {'usuario_id': usuario_id, 'corrida':corrida, 'passageiros_corrida':passageiros_corrida}
    return render(request, 'condutor/avalia_passageiros_corrida.html', context)

def recalcula_media_passageiro(passageiro_id):
    passageiro = get_object_or_404(Passageiro, pk=passageiro_id)
    avaliacoes = Avaliacao_Passageiro.objects.filter(avaliado=passageiro.id)
    nota_media = np.mean([item.nota for item in avaliacoes ])
    passageiro.nota_media = nota_media
    passageiro.save()

