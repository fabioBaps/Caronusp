from rest_framework import generics

from accounts.models import Carona
from .serializers import CaronaSerializer


class CaronaList(generics.ListAPIView):
    queryset = Carona.objects.all()
    serializer_class = CaronaSerializer


class CaronaDetail(generics.RetrieveAPIView):
    queryset = Carona.objects.all()
    serializer_class = CaronaSerializer