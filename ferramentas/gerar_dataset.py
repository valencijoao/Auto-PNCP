import json
from pathlib import Path
import pandas as pd
import hashlib

PASTA_COMPRAS = Path("dados/compras")

from util.portais import identificar_portal

def gerar_id_interno(cnpj, ano, sequencial, portal):
    """
    Gera um identificador interno determinístico para uma contratação.
    """

    base = f"{cnpj}-{ano}-{sequencial}"

    hash_id = hashlib.sha256(
        base.encode("utf-8")
    ).hexdigest()[:12]

    return f"{portal}-{hash_id.upper()}"



def carregar_compra(pasta):
    """
    Carrega os arquivos JSON de uma compras.
    """

    dados = {}

    for arquivo in pasta.glob("*.json"):

        with open(
            arquivo,
            encoding="utf-8"
        ) as f:

            dados[arquivo.stem] = json.load(f)

    return dados


def extrair_dados_compra(compra):
    """
    Extrai os dados necessários de uma contratação.
    """

    dados = compra.get("dados",{})

    cnpj = dados.get("orgaoEntidade",{}).get("cnpj")
    ano_compra = dados.get("anoCompra")
    sequencial_compra = dados.get("sequencialCompra")

    link_portal = dados.get("linkSistemaOrigem")

    origem = identificar_portal(
        link_portal
    )

    if origem is None:
        origem = dados.get(
            "unidadeOrgao",{}
        ).get("ufSigla"
    )

    id_interno = gerar_id_interno(
        cnpj,
        ano_compra,
        sequencial_compra,
        origem
    )

    numero_compra = dados.get("numeroCompra")

    if numero_compra and ano_compra:
        id_processo = f"{numero_compra}/{ano_compra}"
    else:
        id_processo = None

    orgao = dados.get("orgaoEntidade", {})
    cnpj = orgao.get("cnpj")
    nome_orgao = orgao.get("razaoSocial")
    esfera = orgao.get("esferaId")

    unidade = dados.get("unidadeOrgao", {})
    estado = unidade.get("ufNome")
    nome_unidade = unidade.get("nomeUnidade")
    municipio = unidade.get("municipioNome")

    valor_estimado = dados.get("valorTotalEstimado")
    valor_homologado = dados.get("valorTotalHomologado")

    data_publicacao = dados.get("dataPublicacaoPncp")
    data_disputa = dados.get("dataEncerramentoProposta")

    modalidade = dados.get(
        "modalidadeNome"
    )

    modo_disputa = dados.get(
        "modoDisputaNome"
    )

    situacao = dados.get(
        "situacaoCompraNome"
    )

    srp = dados.get(
        "srp"
    )


    return {
        "ID_INTERNO": id_interno,
        "ID": id_processo,
        "NUMERO_COMPRA": numero_compra,
        "ANO_COMPRA": ano_compra,
        "SEQUENCIAL_COMPRA": sequencial_compra,
        "CNPJ": cnpj,
        "ORGAO": nome_orgao,
        "ESFERA": esfera,
        "MUNICIPIO": municipio,
        "VALOR_ESTIMADO": valor_estimado,
        "VALOR_HOMOLOGADO": valor_homologado,
        "DATA_PUBLICACAO": data_publicacao,
        "DATA_DISPUTA": data_disputa,
        "MODALIDADE": modalidade,
        "MODO_DISPUTA": modo_disputa,
        "SITUACAO": situacao,
        "SRP": srp,
        "LINK_PNCP": None,
        "LINK_PORTAL": link_portal,
        "PORTAL": origem
    }







if __name__ == "__main__":

    pasta = Path(
        "dados/compras/39215827000158-2026-8"
    )

    compra = carregar_compra(pasta)

    registro = extrair_dados_compra(
        compra
    )

    print(registro)
