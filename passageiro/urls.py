from django.urls import path

from . import views

app_name = 'passageiro'

urlpatterns = [
    path('<int:usuario_id>/', views.initial, name='initial'),
    path('<int:usuario_id>/edit/', views.UpdateView, name='edit'),
    path('<int:usuario_id>/search/', views.Search_RequestView, name='search'),
    path('<int:usuario_id>/request/<int:corrida_id>/', views.Search_RequestView, name='request'),
    path('<int:usuario_id>/list/<str:aceito>/', views.ListView, name='list-accepted'),
    path('<int:usuario_id>/list/<str:aceito>/', views.ListView, name='list-requested'),
    path('<int:usuario_id>/list/<str:aceito>/', views.ListView, name='list-rejected'),
    path('<int:usuario_id>/list/<str:aceito>/', views.ListView, name='list-ended'),
    path('<int:usuario_id>/racedetail/<int:corrida_id>/', views.DetailView, name='detail'),
    path('<int:usuario_id>/leave/<int:corrida_id>/', views.LeaveView, name='leave'),
    path('<int:usuario_id>/in/<int:corrida_id>/rates/', views.AvaliacaoView, name='rate')
]