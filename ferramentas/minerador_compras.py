from ferramentas.cliente_api import executar_endpoint
from util.cache import salvar_compra



def tentar_endpoint(endpoint, path=None, query=None):
    """
    Executa um endpoint opcional.
    Se falhar, retorna None e continua a coleta.
    """

    try:
        return executar_endpoint(
            endpoint,
            path=path,
            query=query
        )

    except Exception as e:
        print(f"Falha em {endpoint}")
        print(e)
        return None


def baixar_compra_completa(cnpj, ano, sequencial):
    """
    Baixa todas as informações disponíveis de uma contratação.
    """

    path = {
        "cnpj": cnpj,
        "ano": ano,
        "sequencial": sequencial
    }

    print("\n=== Baixando contratação ===")

    #
    # ENDPOINTS OBRIGATÓRIOS
    #

    dados = executar_endpoint(
        "consulta/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}",
        path=path
    )

    itens = executar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens",
        path=path
    )

    #
    # ENDPOINTS OPCIONAIS
    #

    arquivos = tentar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/arquivos",
        path=path
    )

    historico = tentar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/historico",
        path=path
    )

    fontes_orcamentarias = tentar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/fonte-orcamentaria",
        path=path
    )

    compra = {
        "dados": dados,
        "itens": itens,
        "arquivos": arquivos,
        "historico": historico,
        "fontes_orcamentarias": fontes_orcamentarias
    }

    salvar_compra(
        cnpj,
        ano,
        sequencial,
        compra
    )

    return compra


if __name__ == '__main__':

    baixar_compra_completa(
        39215827000158,
        2026,
        8
    )

    