from django.urls import path
from .views import CaronaDetail, CaronaList

urlpatterns = [
    path('carona/<int:pk>/', CaronaDetail.as_view()),
    path('carona/', CaronaList.as_view()),
]