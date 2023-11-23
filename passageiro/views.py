from django.shortcuts import render

def initial(request, usuario_id):
    context = {'usuario_id': usuario_id}
    return render(request, 'passageiro/initial.html', context)