from typing import Optional
from django.conf import settings
from rest_framework.permissions import BasePermission

class FixedTokenPermission(BasePermission):
    """
    Permite acesso se o header contiver o token fixo configurado em
    settings.PROMOCAO_FIXED_TOKEN. Caso contrário, cai no fluxo padrão
    (requer usuário autenticado via DRF Token).

    Aceita os seguintes headers, nesta ordem:
    - Authorization: Token <valor>
    - Authorization: Bearer <valor>
    - X-API-Key: <valor>
    """

    def _extract_token(self, request) -> str:
        auth = (request.headers.get('Authorization') or '').strip()
        if auth.lower().startswith('token '):
            return auth[6:].strip()
        if auth.lower().startswith('bearer '):
            return auth[7:].strip()
        api_key = (request.headers.get('X-API-Key') or '').strip()
        return api_key

    def has_permission(self, request, view) -> bool:
        expected: Optional[str] = getattr(settings, 'PROMOCAO_FIXED_TOKEN', None)
        provided = self._extract_token(request)

        # Autoriza se o token fixo estiver configurado e o header bater
        if expected and provided and provided == expected:
            return True

        # Senão, utiliza o comportamento padrão: requer usuário autenticado
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated)
