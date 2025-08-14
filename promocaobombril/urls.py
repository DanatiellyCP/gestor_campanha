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
    path('regulamento/', views.regulamento, name='regulamento'),
    path('logar/', views.logar, name='logar'),
    path('logout/', views.logout_view, name='logout'),
    path('painel-home/', views.painel_home, name='painel_home'),
    path('painel-cadastrar-cupom/', views.painel_cadastrar_cupom, name='painel_cadastrar_cupom'),
    path('painel-detalhes-cupom/', views.painel_detalhes_cupom, name='painel_detalhes_cupom'),
    path('cadastrar-cupom/<int:id_participante>/', views.cadastrar_cupom, name='cadastrar_cupom'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('cpf-invalido/', views.cpf_invalido_check, name='cpf_invalido_check'),
]
