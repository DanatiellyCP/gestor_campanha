# participantes/urls.py

from django.urls import path, include
from . import views, api_views

# A linha 'app_name' foi removida para eliminar a necessidade de namespaces nos templates.
# Agora, as URLs podem ser chamadas diretamente pelo nome (ex: 'home_participantes').

urlpatterns = [
    # --- URLs para Páginas e Templates ---
    #path('participante/', views.participante, name='participante'),
    path('home_participantes/', views.home_participantes, name='home_participantes'),
    path('regulamento/', views.regulamento, name='regulamento'),
    path('FAQ/', views.FAQ, name='FAQ'),
    path('resultados/', views.resultados, name='resultados'),
    path('como_participar/', views.como_participar, name='como_participar'),
    path('login-e-cadastro/', views.login_e_cadastro, name='login_e_cadastro'),

    path('editar_particip/<int:id>/', views.editar_particip, name='editar_particip'),
    
    path('login_participante/', views.login_participante, name='login_participante'),
    path('cadastrar_participante/', views.cadastrar_participante, name='cadastrar_participante'),
    path('painel_participante/', views.painel_participante, name='painel_participante'),
    path('cupons_participante/<int:id_cupom>/', views.cupons_participante, name='cupons_participante'),
    path('dados_cupons/<int:id_cupom>/', views.dados_cupom, name='dados_cupom'),
     path('area_cupom/<int:id>/', views.area_cupom, name="area_cupom"),

    # --- URLs para a API ---
    path(
        'api/participantes/buscar/', 
        api_views.BuscarParticipanteView.as_view(), 
        name='api_buscar_participante'
    ),
    path(
        'api/participantes/cupons-por-celular/',
        api_views.BuscarCuponsPorCelularView.as_view(),
        name='api_cupons_por_celular'
    ),
]