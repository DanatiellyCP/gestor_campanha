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
    #path('editar_participante/<int:id>', views.editar_participante, name='editar_participante'),
    path('editar_participante/', views.editar_participante, name='editar_participante'),
    path('participante_detalhado/<int:id>', views.participante_detalhado, name='participante_detalhado'),
    path('pesquisar_participante/', views.pesquisar_participante, name='pesquisar_participante'),
    path('deletar_participante/<int:id>', views.deletar_participante, name='deletar_participante'),

    # parte de gestão de SKUs
    path('deletar_skus/', views.deletar_skus, name='deletar_skus'),
   

    #Parte dos Cupons
    path('cupons_enviados/', views.cupons_enviados, name='cupons_enviados'),
    
    # Login e Logout (seguros e corretos)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(), name='logout'),


    # gestão da campanha
    path('gerar_lista_csv/', views.gerar_lista_csv, name='gerar_lista_csv'),
    path('editar_regra/', views.editar_regra, name='editar_regra'),

    path('sorteios/', views.sorteios, name='sorteios'),

    path('dashboard/', views.dash, name='dashboard'),
    path('graficos_participantes/', views.graficos_participantes, name='graficos_participantes'),
    path('participantes-dados/', views.participantes_dados, name='participantes_dados'),
    path('listagem_sorteio/', views.listagem_sorteio, name='listagem_sorteio'),
]
