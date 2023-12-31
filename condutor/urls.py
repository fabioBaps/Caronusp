from django.urls import path

from . import views

app_name = 'condutor'

urlpatterns = [
    path('<int:usuario_id>', views.initial, name='initial'),
    path('<int:usuario_id>/edit/', views.UpdateView, name='edit_perfil'),
    path('<int:usuario_id>/create_carona', views.create_carona, name='create_carona'),
    path('<int:usuario_id>/list_corridas', views.list_corridas, name='list_corridas'),
    path('<int:usuario_id>/carona/<int:carona_id>', views.detail_carona, name='detail_carona'),
    path('<int:usuario_id>/notificacoes/<int:notificacao_id>', views.read_notificacao, name='read_notificacao'),
    path('<int:usuario_id>/carona/<int:carona_id>/edit', views.edit_carona, name='edit_carona'),
    path('<int:usuario_id>/carona/<int:carona_id>/edit', views.edit_carona, name='edit_carona'),
    path('<int:usuario_id>/corrida/<int:corrida_id>/delete', views.delete_corrida, name='delete_corrida'),
    path('<int:usuario_id>/carona/<int:carona_id>/create_corrida', views.create_corrida, name='create_corrida'),
    path('<int:usuario_id>/corrida/<int:corrida_id>/aceitar_passageiro_corrida/<int:passageiro_id>', views.aceitar_passageiro_corrida, name='aceitar_passageiro_corrida'),
    path('<int:usuario_id>/corrida/<int:corrida_id>/rejeitar_passageiro_corrida/<int:passageiro_id>', views.rejeitar_passageiro_corrida, name='rejeitar_passageiro_corrida'),
    path('<int:usuario_id>/corrida/<int:corrida_id>/encerrar_corrida', views.encerrar_corrida, name='encerrar_corrida'),
    path('<int:usuario_id>/corrida/<int:corrida_id>/avalia_passageiro_individual/<int:passageiro_id>', views.avalia_passageiro_individual, name='avalia_passageiro_individual'),
    path('<int:usuario_id>/passageirodetail/<int:passageiro_id>', views.passageirodetail, name='passageirodetail'),
]