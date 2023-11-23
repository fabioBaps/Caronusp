from django.urls import path

from . import views

app_name = 'passageiro'

urlpatterns = [
    path('<int:usuario_id>', views.initial, name='initial'),
]