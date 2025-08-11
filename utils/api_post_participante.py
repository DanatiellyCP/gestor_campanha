import requests

url = "http://127.0.0.1:8000/api/participantes/"
token = "XXXXXXXXXXXXXX"

headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

payload = {
    "nome": "Maria Silva",
    "dt_nasc": "1995-08-20",
    "cpf": "12345678900",
    "celular": "11988887777",
    "email": "maria@email.com",
    "uf": "SP",
    "cidade": "São Paulo",
    "cep": "01001000",
    "rua": "Rua das Flores",
    "bairro": "Centro",
    "num": 123,
    "senha": "12345"
}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.json())
