from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter


# Import do ViewSet para o router da API
from participantes.api_views import ParticipantesViewSet

# --- Configuração do Router da API ---
# O router é ótimo para criar rapidamente os endpoints de CRUD (Create, Read, Update, Delete)
router = DefaultRouter()
#router.register(r'participantes', ParticipantesViewSet)
router.register(r'participantes', ParticipantesViewSet, basename='participantes')

# --- Padrões de URL do Projeto ---
urlpatterns = [
    # Includes para cada app. Cada app gerencia suas próprias URLs.

    path('usuarios/', include('usuarios.urls')),
    path('participantes/', include('participantes.urls')), # Esta linha já inclui nossa nova URL da API
    path('cupons/', include('cupons.urls')),
    path('skus_validos/', include('skus_validos.urls')),
    path('', include('promocaobombril.urls')),

    # --- URLs Globais da API ---
    # Endpoint para obter o token de autenticação
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # Inclui as URLs geradas automaticamente pelo router (ex: /api/participantes/)
    path('api/', include(router.urls)),

    # REMOVIDO: A linha abaixo foi removida por ser redundante e usar uma view que não existe mais.
    # A rota correta agora está dentro de 'participantes/urls.py' e é incluída acima.
    # path('api/participantes/buscar-por-celular/', BuscarParticipantePorCelularView.as_view()),

    # URL do painel de administração do Django
    path('admin/', admin.site.urls),
   
]

# Configuração para servir arquivos de mídia em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)