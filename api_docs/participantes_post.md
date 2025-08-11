# 📝 Cadastrar Participante

**URL:** `/api/participantes/`  
**Método:** `POST`  
**Autenticação:** Token (`Authorization: Token <seu_token>`)

---

## 🎯 Descrição
Este endpoint permite cadastrar um novo participante no sistema.  
Somente usuários autenticados podem realizar esta operação.

---

## 🔐 Autenticação
O Token deve ser enviado no cabeçalho da requisição:

```http
Authorization: Token SEU_TOKEN_AQUI

# 📥 Corpo da Requisição
- Formato: application/json

'''
    {
  "nome": "Maria Silva",
  "dt_nasc": "1995-08-20",
  "cpf": "12345678900",
  "telefone": "1122334455",
  "celular": "11988887777",
  "email": "maria@email.com",
  "uf": "SP",
  "cidade": "São Paulo",
  "cep": "01001000",
  "rua": "Rua das Flores",
  "bairro": "Centro",
  "num": 123
}

'''

| Campo      | Tipo    | Obrigatório | Descrição                         |
| ---------- | ------- | ----------- | --------------------------------- |
| `nome`     | string  | Sim         | Nome completo do participante     |
| `dt_nasc`  | date    | Sim         | Data de nascimento (`YYYY-MM-DD`) |
| `cpf`      | string  | Sim         | CPF (somente números)             |
| `celular`  | string  | Sim         | Celular (somente números)         |
| `email`    | string  | Não         | E-mail do participante            |
| `uf`       | string  | Sim         | Sigla do estado (ex: `SP`)        |
| `cidade`   | string  | Sim         | Nome da cidade                    |
| `cep`      | string  | Sim         | CEP (somente números)             |
| `rua`      | string  | Sim         | Nome da rua                       |
| `bairro`   | string  | Sim         | Bairro                            |
| `num`      | integer | Sim         | Número do endereço                |
| `senha`    | string  | Sim         | senha                             |

## 📤 Respostas
- ✅ 201 Created

'''
    {
  "id": 1,
  "nome": "Maria Silva",
  "dt_nasc": "1995-08-20",
  "cpf": "12345678900",
  "telefone": "1122334455",
  "celular": "11988887777",
  "email": "maria@email.com",
  "uf": "SP",
  "cidade": "São Paulo",
  "cep": "01001000",
  "rua": "Rua das Flores",
  "bairro": "Centro",
  "num": 123
}

'''

## ❌ 400 Bad Request

'''
    {
  "cpf": ["Este campo deve ser único."]
}

'''

## ❌ 401 Unauthorized
'''
    {
  "detail": "Authentication credentials were not provided."
}

'''

## 📌 Exemplo de Requisição com curl
'''
    curl -X POST http://127.0.0.1:8000/api/participantes/ \
     -H "Authorization: Token SEU_TOKEN_AQUI" \
     -H "Content-Type: application/json" \
     -d '{
           "nome": "Maria Silva",
           "dt_nasc": "1995-08-20",
           "cpf": "12345678900",
           "telefone": "1122334455",
           "celular": "11988887777",
           "email": "maria@email.com",
           "uf": "SP",
           "cidade": "São Paulo",
           "cep": "01001000",
           "rua": "Rua das Flores",
           "bairro": "Centro",
           "num": 123
         }'

'''

## 🐍 Exemplo de Requisição com Python
'''
    import requests

url = "http://127.0.0.1:8000/api/participantes/" # aqui subistituir pelo dominio correto
token = "SEU_TOKEN_AQUI"

headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

payload = {
    "nome": "Maria Silva",
    "dt_nasc": "1995-08-20",
    "cpf": "12345678900",
    "telefone": "1122334455",
    "celular": "11988887777",
    "email": "maria@email.com",
    "uf": "SP",
    "cidade": "São Paulo",
    "cep": "01001000",
    "rua": "Rua das Flores",
    "bairro": "Centro",
    "num": 123
}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.json())

'''