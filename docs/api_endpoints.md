# API - Promoção Bombril

Este documento descreve os endpoints de consulta e de envio de notas adicionados ao sistema. Todos exigem autenticação via Token fixo (service-to-service) ou usuário autenticado do DRF. O método recomendado é o Token fixo, configurado em `gestor_campanha/settings.py` como `PROMOCAO_FIXED_TOKEN`.

- Ambientes exemplo:
  - Local: `http://localhost:8000`
  - Produção: `https://promocaobombril.com.br`

- Cabeçalho de autenticação (use um dos formatos):
  - `Authorization: Token <PROMOCAO_FIXED_TOKEN>`
  - `Authorization: Bearer <PROMOCAO_FIXED_TOKEN>`
  - `X-API-Key: <PROMOCAO_FIXED_TOKEN>`

Observação: o número de celular no banco costuma estar salvo com DDI 55. Os endpoints já tentam com e sem `55` automaticamente.

---

## 1) Buscar participante

- Path: `/participantes/api/participantes/buscar/`
- Método: `POST`
- Auth: Token fixo
- Conteúdo: `application/json`
- Body (um dos campos):
  - `cpf` (string)
  - `email` (string)
  - `celular` (string, apenas dígitos, ex.: `5582987124616`)

Exemplo (local):

```bash
curl -i -X POST \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"celular":"5582987124616"}' \
  http://localhost:8000/participantes/api/participantes/buscar/
```

Resposta (200):
```json
{
  "success": true,
  "message": "Participante encontrado.",
  "data": [ { "id": 1, "nome": "...", "cpf": "...", ... } ]
}
```

---

## 2) Listar códigos de sorteio do participante (por celular)

- Path: `/participantes/api/participantes/cupons-por-celular/`
- Método: `POST`
- Auth: Token fixo
- Conteúdo: `application/json`
- Body:
  - `celular` (string)

Exemplo (produção):

```bash
curl -i -X POST \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"celular":"5582987124616"}' \
  https://promocaobombril.com.br/participantes/api/participantes/cupons-por-celular/
```

Resposta (200):
```json
{
  "success": true,
  "message": "5 código(s) encontrado(s).",
  "data": ["1234567890123", "9876543210001", "..."]
}
```

---

## 3) Enviar nota (44 dígitos, imagem completa ou QR)

- Path: `/participantes/api/participantes/enviar-nota/`
- Método: `POST`
- Auth: Token fixo
- Parsers: `multipart/form-data` ou `application/json`
- Identificação do participante: `celular` (obrigatório)
- Formas de enviar a nota (um dos itens):
  1) Chave de 44 dígitos: `chave_acesso` (ou `chave`)
  2) Imagem do QR code:
     - Arquivo: `imagem_qrcode` (multipart)
     - Base64: `imagem_qrcode_base64` (data URL ou base64 puro)
  3) Imagem da nota completa:
     - Arquivo: `imagem_nota` (ou `imagem`) (multipart)
     - Base64: `imagem_nota_base64` (ou `imagem_base64`) (data URL ou base64 puro)

Exemplos:

a) JSON com chave 44 dígitos (local)
```bash
curl -i -X POST \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"celular":"5582987124616","chave_acesso":"99999999999999999999999999999999999999999999"}' \
  http://localhost:8000/participantes/api/participantes/enviar-nota/
```

b) Multipart com arquivo do QR (produção)
```bash
curl -i -X POST \
  -H "Authorization: Token <TOKEN>" \
  -F "celular=5582987124616" \
  -F "imagem_qrcode=@/caminho/para/qrcode.jpg" \
  https://promocaobombril.com.br/participantes/api/participantes/enviar-nota/
```

c) JSON com QR em base64 (data URL)
```bash
curl -i -X POST \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "celular":"5582987124616",
        "imagem_qrcode_base64":"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
      }' \
  http://localhost:8000/participantes/api/participantes/enviar-nota/
```

d) JSON com imagem da nota em base64 (puro)
```bash
curl -i -X POST \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "celular":"5582987124616",
        "imagem_nota_base64":"/9j/4AAQSkZJRgABAQ..."
      }' \
  http://localhost:8000/participantes/api/participantes/enviar-nota/
```

Resposta de sucesso (200):
```json
{
  "success": true,
  "message": "Cupom cadastrado com sucesso.",
  "data": {
    "cupom_id": 123,
    "numeros_da_sorte": ["1234567890123", "9876543210001"],
    "msg_produto": "..."
  }
}
```

Erros comuns (200 com `success:false`):
- `Campo 'celular' é obrigatório.`
- `Chave de acesso inválida ou não encontrada (esperado 44 dígitos).`
- `Participante não encontrado pelo celular informado.`

---

## 4) Listagem (opcional) via ViewSet padrão do DRF

- Path: `/api/participantes/` (router DRF)
- Método: `GET`
- Auth: Token fixo (aceito pela permission) ou Token DRF por usuário

Exemplo:
```bash
curl -i -X GET \
  -H "Authorization: Token <TOKEN>" \
  http://localhost:8000/api/participantes/
```

---

## Autenticação e Segurança

- O token fixo deve ser mantido em segredo, configurado via variável de ambiente:
  - `PROMOCAO_FIXED_TOKEN=<seu_token>`
- Sempre usar HTTPS em produção.
- Rate limiting e rotação de token são boas práticas (não incluídas aqui).

---

## Contato

Em caso de dúvidas ou para estender os endpoints (filtros adicionais, payloads mais ricos), entre em contato com a equipe de desenvolvimento.
