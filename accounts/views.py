from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Usuario, Condutor, Passageiro
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('first_name','last_name','telefone', 'RG', 'email', 'foto')

def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:afterlogin', args=(request.user.id, )))
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            authenticated_user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('accounts:afterlogin', args=(user.id, )))
    else:
        form = UsuarioCreationForm()

    context = {'form': form}
    return render(request, 'accounts/signup.html', context)

@login_required
def afterlogin(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    context = {'usuario': usuario}
    return render(request, 'registration/afterlogin.html', context)

def signCondutor(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == "POST":
        usuario.is_condutor = True
        usuario.save()
        condutor = Condutor(usuario=usuario, nota_media=5.0, CNH=request.POST['CNH'])
        condutor.save()
        return HttpResponseRedirect(
            reverse('condutor:initial', args=(usuario.id, )))
        
    context = {'usuario': usuario}
    return render(request, 'accounts/signcondutor.html', context)
    
def signPassageiro(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == "POST":
        usuario.is_passageiro = True
        usuario.save()
        passageiro = Passageiro(usuario=usuario, nota_media=5.0)
        passageiro.save()
        return HttpResponseRedirect(
            reverse('passageiro:initial', args=(usuario.id, )))
    context = {'usuario': usuario}
    return render(request, 'registration/afterlogin.html', context)
    
def my_view(request):
    usuario = request.user
    return HttpResponseRedirect(reverse_lazy('accounts:afterlogin', args=(usuario.id, ))) 
    