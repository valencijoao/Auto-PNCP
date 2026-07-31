import re
import json
import requests


from api.session import criar_sessao

link = "https://pncp.gov.br/app/editais/22980973000177/2026/113"

padrao = r"editais/(\d+)/(\d+)/(\d+)"

resultado = re.search(padrao, link)

if not resultado:
    raise Exception("Link inválido.")

cnpj, ano, sequencial = resultado.groups()

url = (
    f"https://pncp.gov.br/api/consulta/v1/orgaos/"
    f"{cnpj}/compras/{ano}/{sequencial}"
)

session = criar_sessao()

try:
    r = session.get(url, timeout=60)

    print("Status:", r.status_code)

    r.raise_for_status()

    dados = r.json()

    with open("chaves.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    print("Arquivo chaves.json gerado com sucesso!")

except requests.exceptions.ReadTimeout:
    print("A API do PNCP demorou para responder (timeout).")

except requests.exceptions.HTTPError as e:
    print(f"Erro HTTP: {e}")

except requests.exceptions.RequestException as e:
    print(f"Erro de conexão: {e}")