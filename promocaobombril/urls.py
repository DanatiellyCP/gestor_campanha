from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.participe, name='participe'),
    path('home_responsive/', views.home_responsive, name='home_responsive'),
    path('como-participar/', views.como_participar, name='como_participar'),
    path('produtos/', views.produtos, name='produtos'),
    path('lista-resultados/', views.lista_resultado, name='lista_resultado'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('duvidas/', views.duvidas, name='duvidas'),
    path('logar/', views.logar, name='logar'),
    path('painel-home/', views.painel_home, name='painel_home'),
    path('painel-cadastrar-cupom/', views.painel_cadastrar_cupom, name='painel_cadastrar_cupom'),
]
