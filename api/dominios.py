import json
from pathlib import Path

from api.session import criar_sessao

BASE = "https://pncp.gov.br/api/consulta/v1"
PASTA = Path('dados')
PASTA.mkdir(exist_ok=True)

session = criar_sessao()


def extrair_lista(dados):
    """
    Encontra automaticamente onde está a lista de registros.
    """

    # Caso 1: já é uma lista
    if isinstance(dados, list):
        return dados

    # Caso 2: é um dicionário
    if isinstance(dados, dict):

        # Procura a primeira lista dentro do dicionário
        for valor in dados.values():
            if isinstance(valor, list):
                return valor

    return []


def converter_para_dicionario(lista):
    """
    Converte uma lista de objetos em um dicionário
    {codigo: descricao}.
    """

    resultado = {}

    for item in lista:

        if not isinstance(item, dict):
            continue

        codigo = None

        # procura possíveis nomes do código
        for chave in (
            "codigo",
            "id",
            "valor",
            "sequencial",
            "numero"
        ):
            if chave in item:
                codigo = item[chave]
                break

        descricao = None

        # procura possíveis nomes da descrição
        for chave in (
            "nome",
            "descricao",
            "titulo",
            "texto",
            "descricaoResumida"
        ):
            if chave in item:
                descricao = item[chave]
                break

        if codigo is not None and descricao:
            resultado[str(codigo)] = descricao

    return resultado


def baixar_dominio(endpoint, arquivo_saida):

    url = f"{BASE}/{endpoint}"

    print(f"Consultando {endpoint}...")

    resposta = session.get(url, timeout=60)
    resposta.raise_for_status()

    dados = resposta.json()

    lista = extrair_lista(dados)

    print(f"{len(lista)} registros encontrados.")

    dicionario = converter_para_dicionario(lista)

    caminho = PASTA / arquivo_saida

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(
            dicionario,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"{arquivo_saida} salvo com {len(dicionario)} registros.\n")


def atualizar_dominios():

    dominios = {
        "modalidades": "modalidades.json",
        "modos-disputas": "modos_disputa.json",
        "criterios-julgamentos": "criterios.json",
        "amparos-legais": "amparos_legais.json",
        "tipos-instrumentos-convocatorios": "instrumentos.json",
        "tipos-contratos": "contratos.json",
    }

    for endpoint, arquivo in dominios.items():

        try:
            baixar_dominio(endpoint, arquivo)

        except Exception as e:
            print(f"Erro em {endpoint}: {e}")