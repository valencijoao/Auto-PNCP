import json
from pathlib import Path
from urllib.parse import urlparse

from config.caminhos import DADOS

CAMINHO_TRATADOS = DADOS / "portais_tratados.json"
CAMINHO_PADRAO = DADOS / "portais.json"

with open(CAMINHO_PADRAO, 'r', encoding='utf-8') as arquivo:
    PORTAIS = json.load(arquivo)

with open(CAMINHO_TRATADOS, 'r', encoding='utf-8') as arquivo:
    PORTAIS_TRATADOS = json.load(arquivo)
# levantamento de portais não cadastrados

PORTAIS_DESCONHECIDOS = set()

def identificar_portal(link):
    """
    Retorna o nome do portal a partir da URL cadastrada no arquivo JSON.
    """

    if not link:
        return None
    
    
    dominio = urlparse(link).netloc.lower()

    for dominio_base, nome in PORTAIS.items():

        if dominio.endswith(dominio_base):
            return nome
            
    PORTAIS_DESCONHECIDOS.add(dominio)
    
    return None


def traduzir_portal(portal):
    """
    Traduz o código do portal para o nome correspondente.
    """

    if not portal:
        return None

    return PORTAIS_TRATADOS.get(
        portal,
        portal
    )


def listar_desconhecidos():
    """
    Exibe os portais encontrados que ainda não existem
    no arquivo JSON
    """

    if not PORTAIS_DESCONHECIDOS:
        return
    
    print('\nPORTAIS NÃO CADASTRADOS:')

    for portal in sorted(PORTAIS_DESCONHECIDOS):
        print(portal)


def obter_origem(dados):
    """
    Obtém a origem da contratação.

    Prioriza o portal identificado pelo link do sistema de origem.
    Caso não exista, utiliza a UF da unidade do órgão.
    """

    link_portal = dados.get(
        "linkSistemaOrigem"
    )

    origem = identificar_portal(
        link_portal
    )

    if origem is None:

        origem = dados.get(
            "unidadeOrgao",
            {}
        ).get(
            "ufSigla"
        )

    return origem