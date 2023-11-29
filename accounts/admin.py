from django.contrib import admin

from .models import Usuario, Condutor, Passageiro, Carona, Corrida, Passageiros_corrida, Avaliacao_Condutor, Avaliacao_Passageiro, Mensagem, Notificacao

admin.site.register(Usuario)
admin.site.register(Condutor)
admin.site.register(Passageiro)
admin.site.register(Carona)
admin.site.register(Corrida)
admin.site.register(Passageiros_corrida)
admin.site.register(Avaliacao_Condutor)
admin.site.register(Avaliacao_Passageiro)
admin.site.register(Mensagem)
admin.site.register(Notificacao)