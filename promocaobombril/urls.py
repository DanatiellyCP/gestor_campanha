from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.participe, name='participe'),
    path('como-participar/', views.como_participar, name='como_participar'),
    path('produtos/', views.produtos, name='produtos'),
    path('lista-resultado/', views.lista_resultado, name='lista_resultado'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('duvidas/', views.duvidas, name='duvidas'),
    path('logar/', views.logar, name='logar'),
]
