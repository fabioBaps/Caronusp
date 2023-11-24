from django.contrib import admin

from .models import Usuario, Condutor, Passageiro

admin.site.register(Usuario)
admin.site.register(Condutor)
admin.site.register(Passageiro)