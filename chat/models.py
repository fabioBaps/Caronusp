from django.shortcuts import render

def chat_corrida(request, corrida_id):
    # Lógica do chat aqui
    return render(request, 'chat/chat_corrida.html', {'corrida_id': corrida_id})
