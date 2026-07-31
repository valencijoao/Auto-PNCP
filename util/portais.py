import json
from pathlib import Path
from urllib.parse import urlparse

CAMINHO_JSON = Path(__file__).parent.parent / "dados" / "portais.json"

with open(CAMINHO_JSON, 'r', encoding='utf-8') as arquivo:
    PORTAIS = json.load(arquivo)

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

        