from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('<int:usuario_id>/', views.afterlogin, name='afterlogin'),
    path('signup/condutor/<int:usuario_id>/', views.signCondutor, name='condutor'),
    path('signup/passageiro/<int:usuario_id>/', views.signPassageiro, name='passageiro'),
]