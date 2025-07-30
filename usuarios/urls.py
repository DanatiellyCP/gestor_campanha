## urls do app usuarios

from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('home/', views.home, name='home'),
    path('sistema/', views.sistema, name='sistema'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('dash/', views.dash, name='dash'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('detalhe/<int:id>', views.detalhe, name='detalhe'),
    path('deletar/<int:id>', views.deletar, name='deletar'),
    path('editar/<int:id>', views.editar, name='editar'),
    path('perfil/<int:id>', views.perfil, name='perfil'),
    
    # parte de Participantes e sorteios
    path('dados_participantes/', views.dados_participantes, name='dados_participantes'),
    path('sorteios/', views.sorteios, name='sorteios'),
    path('editar_participante/<int:id>', views.editar_participante, name='editar_participante'),
    path('participante_detalhado/<int:id>', views.participante_detalhado, name='participante_detalhado'),
    path('pesquisar_participante/', views.pesquisar_participante, name='pesquisar_participante'),

    # parte de gestão de SKUs
    path('deletar_skus/', views.deletar_skus, name='deletar_skus'),
   
    
    # Login e Logout (seguros e corretos)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(), name='logout'),
]