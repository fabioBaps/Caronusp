from django.urls import path

from . import views

app_name = 'passageiro'

urlpatterns = [
    path('<int:usuario_id>/', views.initial, name='initial'),
    path('<int:usuario_id>/edit', views.UpdateView, name='edit'),
    path('<int:usuario_id>/search', views.SearchView, name='search'),
]