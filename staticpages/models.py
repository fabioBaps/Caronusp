from django.db import models
from django.conf import settings


class Usuario(models.Model):
    # id = models.IntegerField()
    nome = models.CharField()
    email = models.CharField()
    telefone = models.CharField()
    hash_senha = models.CharField()
    RG = models.CharField()
    foto = models.ImageField()

    def __str__(self):
        return f'{self.nome}'

class Passageiro(models.Model):
    # id = models.IntegerField()
    usuario_id = models.ForeignKey(Usuario)
    nota_media = models.FloatField()

    def __str__(self):
        return f'"{self.id}" - {self.usuario_id}'
    
class Condutor(models.Model):
    # id = models.IntegerField()
    usuario_id = models.ForeignKey(Usuario)
    nota_media = models.FloatField()
    CNH = models.IntegerField()

    def __str__(self):
        return f'"{self.id}" - {self.usuario_id}'

class Carona(models.Model):
    # id = models.IntegerField()
    condutor_id = models.ForeignKey(Condutor)
    local_partida = models.CharField()
    local_chegada = models.CharField()
    horario_partida = models.TimeField()
    horario_chegada = models.TimeField()
    lugares = models.IntegerField()
    placa_veiculo = models.CharField()

    def __str__(self):
        return f''
    
class Corrida(models.Model):
    # id = models.IntegerField()
    carona_id = models.ForeignKey(Carona)
    dia = models.DateField()
    ativa = models.BooleanField()
    vagas = models.IntegerField()

    def __str__(self):
        return f''
    
class Passageiros_corrida(models.Model):
    # id = models.IntegerField()
    passageiro_id = models.ForeignKey(Passageiro)
    corrida_id = models.ForeignKey(Corrida)
    aceito = models.BooleanField()

    def __str__(self):
        return f''

class Avaliacao_Condutor(models.Model):
    # id = models.IntegerField()
    avaliador_id = models.ForeignKey(Passageiro)
    avaliado_id = models.ForeignKey(Condutor)
    corrida_id = models.ForeignKey(Corrida)
    nota = models.IntegerField()

    def __str__(self):
        return f''

class Avaliacao_Passageiro(models.Model):
    # id = models.IntegerField()
    avaliador_id = models.ForeignKey(Condutor)
    avaliado_id = models.ForeignKey(Passageiro)
    corrida_id = models.ForeignKey(Corrida)
    nota = models.IntegerField()

    def __str__(self):
        return f''
    
class Mensagem(models.Model):
    # id = models.IntegerField()
    usuario_id = models.ForeignKey(Usuario)
    corrda_id = models.ForeignKey(Corrida)
    texto = models.CharField()
    hora = models.DateTimeField()

    def __str__(self):
        return f''