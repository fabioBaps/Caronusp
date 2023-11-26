from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is False:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
class Usuario(AbstractUser):
    telefone = models.CharField(max_length=11)
    RG = models.CharField(max_length=9)
    foto = models.ImageField()
    is_condutor = models.BooleanField(default=False)
    is_passageiro = models.BooleanField(default=False)
    objects = UsuarioManager()
    
class Condutor(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nota_media = models.FloatField()
    CNH = models.CharField(max_length=11)
    
    def __str__(self):
        return f'"{self.id}" - {self.usuario}'
    
class Passageiro(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nota_media = models.FloatField()
    
    def __str__(self):
        return f'"{self.id}" - {self.usuario}'
    
class Carona(models.Model):
    condutor = models.ForeignKey(Condutor, on_delete=models.CASCADE)
    local_partida = models.CharField(max_length=100)
    local_chegada = models.CharField(max_length=100)
    horario_partida = models.TimeField()
    horario_chegada = models.TimeField()
    lugares = models.IntegerField()
    placa_veiculo = models.CharField(max_length=7)

    def __str__(self):
        return f'"{self.id}" - {self.condutor} - {self.local_partida} - {self.local_chegada} - {self.horario_partida} - {self.horario_chegada} - {self.lugares} - {self.placa_veiculo}'
    
class Corrida(models.Model):
    carona = models.ForeignKey(Carona, on_delete=models.CASCADE)
    dia = models.DateField()
    ativa = models.BooleanField()
    vagas = models.IntegerField()

    def __str__(self):
        return f'"{self.id}" - {self.carona} - {self.dia} - {self.ativa} - {self.vagas}'

class Passageiros_corrida(models.Model):
    passageiro = models.ForeignKey(Passageiro, on_delete=models.CASCADE)
    corrida = models.ForeignKey(Corrida, on_delete=models.CASCADE)
    aceito = models.BooleanField(null=True)

    def __str__(self):
        return f'"{self.id}" - {self.passageiro} - {self.corrida} - {self.aceito}'

class Avaliacao_Condutor(models.Model):
    avaliador = models.ForeignKey(Passageiro, on_delete=models.CASCADE)
    avaliado = models.ForeignKey(Condutor, on_delete=models.CASCADE)
    corrida = models.ForeignKey(Corrida, on_delete=models.CASCADE)
    nota = models.IntegerField()

    def __str__(self):
        return f'"{self.id}" - {self.avaliador} - {self.avaliado} - {self.corrida} - {self.nota}'
    
class Avaliacao_Passageiro(models.Model):
    avaliador = models.ForeignKey(Condutor, on_delete=models.CASCADE)
    avaliado = models.ForeignKey(Passageiro, on_delete=models.CASCADE)
    corrida = models.ForeignKey(Corrida, on_delete=models.CASCADE)
    nota = models.IntegerField()

    def __str__(self):
        return f'"{self.id}" - {self.avaliador} - {self.avaliado} - {self.corrida} - {self.nota}'
    
class Mensagem(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    corrida = models.ForeignKey(Corrida, on_delete=models.CASCADE)
    texto = models.CharField(max_length=100)
    hora = models.DateTimeField()

    def __str__(self):
        return f'"{self.id}" - {self.usuario} - {self.corrida} - {self.texto} - {self.hora}'
    