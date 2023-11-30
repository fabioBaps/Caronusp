from django.urls import path
from .views import chat_corrida

app_name = 'chat'

urlpatterns = [
    path('<int:usuario_id>/chat_corrida/<int:corrida_id>/<int:type_actor>', chat_corrida, name='chat_corrida'),
]
