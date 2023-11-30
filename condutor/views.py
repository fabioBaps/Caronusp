from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario, Condutor, Carona, Corrida, Passageiros_corrida, Passageiro, Avaliacao_Passageiro, Notificacao
from django.contrib.auth.decorators import login_required
import googlemaps
from _env import GOOGLE_API_KEY
import requests
import numpy as np


def checa_login(request, usuario_id):
    user = request.user
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.is_condutor and usuario.id == user.id:
        return True
    return False
        
@login_required
def initial(request, usuario_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    todas_caronas = Carona.objects.filter(condutor=condutor)
    caronas = []
    for carona in todas_caronas:
        corridas = Corrida.objects.filter(carona=carona, ativa=True)
        if corridas:
            caronas.append(carona)
    notificacoes = Notificacao.objects.filter(usuario=condutor.usuario, para_condutor=True, visto=False)
    context = {'usuario_id': usuario_id, 'caronas':caronas,'notificacoes':notificacoes}
    return render(request, 'condutor/initial.html', context)


@login_required
def UpdateView(request, usuario_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
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
        condutor.CNH = request.POST['CNH']
        condutor.save()
        return HttpResponseRedirect(
            reverse('condutor:initial', args=(usuario.id, )))
    context = {'usuario': usuario, 'condutor': condutor}
    return render(request, 'condutor/edit_perfil.html', context)


@login_required
def create_carona(request, usuario_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    if request.method == "POST":
        carona_dict = {}
        carona_dict['condutor'] = condutor

        api_key = GOOGLE_API_KEY
        chegada = request.POST['local_chegada']
        chegada_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={chegada}&key={api_key}"
        chegada_response = requests.get(chegada_url)
        chegada_data = chegada_response.json()
        chegada_result = chegada_data.get('results', [])
        if chegada_result:
            top_chegada = chegada_result[0]
            carona_dict['endereco_chegada'] = top_chegada.get('formatted_address', '')
            carona_dict['placeId_chegada'] = top_chegada.get('place_id', '')
            carona_dict['local_chegada'] = chegada

        partida = request.POST['local_partida']
        partida_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={partida}&key={api_key}"
        partida_response = requests.get(partida_url)
        partida_data = partida_response.json()
        partida_result = partida_data.get('results', [])
        if partida_result:
            top_partida = partida_result[0]
            carona_dict['endereco_partida'] = top_partida.get('formatted_address', '')
            carona_dict['placeId_partida'] = top_partida.get('place_id', '')
            carona_dict['local_partida'] = partida

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

@login_required
def detail_carona(request, usuario_id, carona_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    carona = get_object_or_404(Carona, pk=carona_id)
    corridas = Corrida.objects.filter(carona=carona, ativa=True)
    info_corridas_passageiros = [get_passageiros(corrida) for corrida in corridas]
    context = {'usuario_id': usuario_id, 'carona':carona, 'info_corridas_passageiros':info_corridas_passageiros}
    return render(request, 'condutor/detail_carona.html', context)

@login_required
def edit_carona(request, usuario_id, carona_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    carona = get_object_or_404(Carona, pk=carona_id)
    if not carona.condutor.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    if request.method == "POST":
        api_key = GOOGLE_API_KEY
        chegada = request.POST['local_chegada']
        chegada_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={chegada}&key={api_key}"
        chegada_response = requests.get(chegada_url)
        chegada_data = chegada_response.json()
        chegada_result = chegada_data.get('results', [])
        if chegada_result:
            top_chegada = chegada_result[0]
            carona.endereco_chegada = top_chegada.get('formatted_address', '')
            carona.placeId_chegada = top_chegada.get('place_id', '')
            carona.local_chegada = chegada

        partida = request.POST['local_partida']
        partida_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={partida}&key={api_key}"
        partida_response = requests.get(partida_url)
        partida_data = partida_response.json()
        partida_result = partida_data.get('results', [])
        if partida_result:
            top_partida = partida_result[0]
            carona.endereco_partida = top_partida.get('formatted_address', '')
            carona.placeId_partida = top_partida.get('place_id', '')
            carona.local_partida = partida

        carona.horario_chegada = request.POST['horario_chegada']
        carona.horario_partida = request.POST['horario_partida']
        carona.placa_veiculo = request.POST['placa']
        carona.save()
        
        corridas_da_carona = Corrida.objects.filter(carona_id=carona_id)
        for corrida in corridas_da_carona:
            passageiros_corrida = Passageiros_corrida.objects.filter(corrida=corrida, aceito=True)
            for passageiro in passageiros_corrida:
                texto_notificação = f'A corrida de {corrida.carona.condutor.usuario.first_name} {corrida.carona.condutor.usuario.last_name} do dia {corrida.dia} foi editada. Veja os detalhes!'
                notificacao = Notificacao(usuario=passageiro.passageiro.usuario, texto=texto_notificação, para_condutor=False)
                notificacao.save()
        
        return HttpResponseRedirect(
            reverse('condutor:detail_carona', args=(usuario_id, carona_id )))
    corridas = Corrida.objects.filter(carona=carona)
    horario_partida_formatado = str(carona.horario_partida)[:-3]
    horario_chegada_formatado = str(carona.horario_chegada)[:-3]
    context = {'usuario_id': usuario_id, 'carona':carona,'corridas':corridas,'horario_partida_formatado':horario_partida_formatado,'horario_chegada_formatado':horario_chegada_formatado}
    return render(request, 'condutor/edit_carona.html', context)

@login_required
def delete_corrida(request, usuario_id, corrida_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    if not corrida.carona.condutor.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    if request.method == "POST":
        passageiros_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, aceito=True)
        for passageiro in passageiros_corrida:
            texto_notificação = f'A corrida de {corrida.carona.condutor.usuario.first_name} {corrida.carona.condutor.usuario.last_name} do dia {corrida.dia} foi cancelada. Procure outra!'
            notificacao = Notificacao(usuario=passageiro.passageiro.usuario, texto=texto_notificação, para_condutor=False)
            notificacao.save()
        corrida.delete()
        return HttpResponseRedirect(
            reverse('condutor:detail_carona', args=(usuario_id, corrida.carona.id )))
    context = {'corrida':corrida}
    return render(request, 'condutor/delete_corrida.html', context)

@login_required
def create_corrida(request, usuario_id, carona_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    carona = get_object_or_404(Carona, pk=carona_id)
    if not carona.condutor.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
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

@login_required
def aceitar_passageiro_corrida(request, usuario_id, corrida_id, passageiro_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    if not corrida.carona.condutor.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    passageiro_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, passageiro=passageiro_id)[0]
    passageiro_corrida.aceito = True
    passageiro_corrida.save()
    corrida.vagas -= 1
    corrida.save()
    carona = get_object_or_404(Carona, pk=corrida.carona.id)
    corridas = Corrida.objects.filter(carona=carona, ativa=True)
    texto_notificação = f'Você foi aceito na corrida de {carona.condutor.usuario.first_name} {carona.condutor.usuario.last_name} do dia {corrida.dia}'
    notificacao = Notificacao(usuario=passageiro_corrida.passageiro.usuario, texto=texto_notificação, para_condutor=False)
    notificacao.save()
    info_corridas_passageiros = [get_passageiros(corrida_) for corrida_ in corridas]
    context = {'usuario_id': usuario_id, 'carona':carona, 'info_corridas_passageiros':info_corridas_passageiros}
    return render(request, 'condutor/detail_carona.html', context)

@login_required
def rejeitar_passageiro_corrida(request, usuario_id, corrida_id, passageiro_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    if not corrida.carona.condutor.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    passageiro_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, passageiro=passageiro_id)[0]
    passageiro_corrida.aceito = False
    passageiro_corrida.save()
    carona = get_object_or_404(Carona, pk=corrida.carona.id)
    corridas = Corrida.objects.filter(carona=carona, ativa=True)
    texto_notificação = f'Você foi rejeitado na corrida de {carona.condutor.usuario.first_name} {carona.condutor.usuario.last_name} do dia {corrida.dia}'
    notificacao = Notificacao(usuario=passageiro_corrida.passageiro.usuario, texto=texto_notificação, para_condutor=False)
    notificacao.save()
    info_corridas_passageiros = [get_passageiros(corrida_) for corrida_ in corridas]
    context = {'usuario_id': usuario_id, 'carona':carona, 'info_corridas_passageiros':info_corridas_passageiros}
    return render(request, 'condutor/detail_carona.html', context)

@login_required
def encerrar_corrida(request, usuario_id, corrida_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    if not corrida.carona.condutor.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    corrida.ativa=False
    corrida.save()
    passageiros_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, aceito=True)
    passageiros_corrida_nao_avaliados = []
    for passageiro in passageiros_corrida:
        try: # ja existe avaliacao?
            get_object_or_404(Avaliacao_Passageiro, corrida_id=corrida_id, avaliado_id=passageiro.passageiro.id)
        except: # se nao, add ele nos nao avaliados e manda notificacao
            passageiros_corrida_nao_avaliados.append(passageiro)
            texto_notificação = f'A corrida de {condutor.usuario.first_name} {condutor.usuario.last_name} do dia {corrida.dia} foi encerrada. Avalie o condutor!'
            notificacao = Notificacao(usuario=passageiro.passageiro.usuario, texto=texto_notificação, para_condutor=False)
            notificacao.save()
    context = {'usuario_id': usuario_id, 'corrida':corrida, 'passageiros_corrida':passageiros_corrida_nao_avaliados}
    return render(request, 'condutor/avalia_passageiros_corrida.html', context)

@login_required
def avalia_passageiro_individual(request, usuario_id, corrida_id, passageiro_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    corrida = get_object_or_404(Corrida, pk=corrida_id)
    if not corrida.carona.condutor.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    passageiro = get_object_or_404(Passageiro, pk=passageiro_id)
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    try:
        get_object_or_404(Avaliacao_Passageiro,corrida=corrida,avaliador=condutor,avaliado=passageiro,nota=nota)
        passageiros_corrida = Passageiros_corrida.objects.filter(corrida=corrida_id, aceito=True)
        context = {'usuario_id': usuario_id, 'corrida':corrida, 'passageiros_corrida':passageiros_corrida}
        return render(request, 'condutor/avalia_passageiros_corrida.html', context)
    except:
        pass
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

@login_required
def read_notificacao(request, usuario_id, notificacao_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    notificacao = get_object_or_404(Notificacao,pk=notificacao_id)
    if not notificacao.usuario.id == request.user.id: return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    notificacao.visto = True
    notificacao.save()
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    caronas = Carona.objects.filter(condutor=condutor)
    notificacoes = Notificacao.objects.filter(usuario=condutor.usuario, para_condutor=True, visto=False)
    context = {'usuario_id': usuario_id, 'caronas':caronas,'notificacoes':notificacoes}
    return render(request, 'condutor/initial.html', context)

@login_required
def list_corridas(request, usuario_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    condutor = get_object_or_404(Condutor, usuario=usuario_id)
    caronas = Carona.objects.filter(condutor=condutor)
    corrida_list = []
    for carona in caronas:
        corridas = Corrida.objects.filter(carona=carona, ativa=False)
        for corrida in corridas:
            corrida_list.append(corrida)
    
    context = {"corrida_list": corrida_list}
    return render(request, 'condutor/list_corridas.html', context)
    
@login_required
def passageirodetail(request, usuario_id, passageiro_id):
    if not checa_login(request, usuario_id): return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id,)))
    passageiro = get_object_or_404(Passageiro, pk=passageiro_id)
    context = {'usuario_id': usuario_id, 'passageiro':passageiro}
    return render(request, 'condutor/detail_passageiro.html', context)
