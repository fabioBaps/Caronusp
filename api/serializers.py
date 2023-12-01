from rest_framework import serializers

from accounts.models import Carona


class CaronaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Carona
        fields = ['id', 'condutor', 'local_partida', 'local_chegada', 'horario_chegada', 'horario_partida', 'lugares', 'placa_veiculo']