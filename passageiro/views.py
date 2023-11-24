from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Usuario
from django.contrib.auth.decorators import login_required

@login_required
def initial(request, usuario_id):
    context = {'usuario_id': usuario_id}
    return render(request, 'passageiro/initial.html', context)

@login_required
def UpdateView(request, usuario_id):
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
    context = {'usuario': usuario}
    return render(request, 'passageiro/edit.html', context)