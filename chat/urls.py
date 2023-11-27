from django.urls import path
from .views import chat_corrida

app_name = 'chat'

urlpatterns = [
    path('chat_corrida/<int:corrida_id>/', chat_corrida, name='chat_corrida'),
]
