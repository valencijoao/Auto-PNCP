import json
from pathlib import Path
import pandas as pd
import hashlib
from config.caminhos import (COMPRAS, DATASETS, CLIENTES)

PASTA_COMPRAS = COMPRAS
PASTA_DATASETS = DATASETS
PASTA_CLIENTES = CLIENTES

from util.portais import identificar_portal, traduzir_portal, obter_origem
from excel.formatacao import formatar_planilha




def gerar_id_interno(cnpj, ano, sequencial, origem):
    """
    Gera um identificador interno determinístico para uma contratação.
    """

    base = f"{cnpj}-{ano}-{sequencial}"

    hash_id = hashlib.sha256(
        base.encode("utf-8")
    ).hexdigest()[:12]

    return f"{origem}-{hash_id.upper()}"



def carregar_compra(pasta):
    """
    Carrega os arquivos JSON de uma compras.
    """

    dados = {}

    for arquivo in pasta.glob("*.json"):

        nome = arquivo.stem

        if nome.startswith("dados"):
            chave = "dados"

        elif nome.startswith("itens"):
            chave = "itens"

        elif nome.startswith("arquivos"):
            chave = "arquivos"

        elif nome.startswith("fontes_orcamentarias"):
            chave = "fontes_orcamentarias"

        elif nome.startswith("historico"):
            chave = "historico"

        elif nome.startswith("clientes"):
            chave = "clientes"

        else:
            chave = nome

        with open(
            arquivo,
            encoding="utf-8"
        ) as f:

            dados[chave] = json.load(f)

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

    link_pncp = f"https://pncp.gov.br/app/editais/{cnpj}/{ano_compra}/{sequencial_compra}"

    origem = obter_origem(
        dados
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
        "ESTADO": estado,
        "UNIDADE": nome_unidade,
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
        "LINK_PNCP": link_pncp,
        "LINK_PORTAL": link_portal,
        "PORTAL": origem
    }


def gerar_dataset():
    """
    Percorre todas as compras e gera o dataset interno.
    """

    registros = []

    for pasta in PASTA_COMPRAS.iterdir():

        if not pasta.is_dir():
            continue

        print(f"\nProcessando compra: {pasta.name}")

        compra = carregar_compra(pasta)

        registro = extrair_dados_compra(compra)

        clientes = compra.get(
            "clientes",
            []
        )

        item = compra.get(
            "item",
            []
        )

        for cliente in clientes:

            registro_cliente = registro.copy()

            registro_cliente["CLIENTE"] = cliente
            registro_cliente["ITEM"] = item


            registros.append(registro_cliente)

    df = pd.DataFrame(registros)

    colunas = list(df.columns)

    colunas.remove("CLIENTE")

    colunas.insert(1, "CLIENTE")

    df = df[colunas]

    return df



def salvar_dataset(df):
    """
    Salva o dataset interno como CSV.
    """

    caminho = PASTA_DATASETS / "dataset_interno.csv"

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nDataset salvo em: {caminho}")

def filtrar_novas_contratacoes(df, novas_contratacoes):
    """
    Retorna somente as contratações incluídas nesta execução.
    """

    df_novas = df[
        df["ID_INTERNO"].isin(novas_contratacoes)
    ].copy()

    return df_novas


def gerar_dataset_cliente(df, cliente):
    """
    Gera o dataset destinado a um cliente específico.
    """

    df_cliente = df[
        df["CLIENTE"] == cliente
    ].copy()

    df_cliente["ID"] = (
        df_cliente["NUMERO_COMPRA"].astype(str)
        + "/"
        + df_cliente["ANO_COMPRA"].astype(str)
    )

    df_cliente["ITEM"] = ""

    df_cliente["PORTAL"] = (
    df_cliente["PORTAL"]
    .apply(traduzir_portal)
    )

    df_cliente["DATA_DISPUTA"] = pd.to_datetime(
        df_cliente["DATA_DISPUTA"],
        errors="coerce"
    ).dt.strftime("%d/%m/%Y")

    df_cliente = df_cliente[
        [
            "CLIENTE",
            "ID",
            "ITEM",
            "MODALIDADE",
            "VALOR_ESTIMADO",
            "ORGAO",
            "DATA_DISPUTA",
            "PORTAL",
            "LINK_PORTAL",
            "LINK_PNCP"
            
        ]
    ]

    return df_cliente


def tratar_valor(x):

    if pd.isna(x):
        return x

    if isinstance(x, str):

        if x.strip().lower() == "sigiloso":
            return "Sigiloso"

        try:
            valor = float(x)
        except ValueError:
            return x

    else:
        valor = x

    if valor == 0:
        return "Sigiloso"

    return x



def salvar_dataset_cliente(df_cliente, cliente):
    """
    Adiciona novas contratações ao dataset existente do cliente.
    """

    caminho = PASTA_CLIENTES / f"{cliente}.xlsx"

    if caminho.exists():

        df_existente = pd.read_excel(
            caminho
        )

        df_cliente = pd.concat(
            [
                df_existente,
                df_cliente
            ],
            ignore_index=True
        )

        df_cliente = df_cliente.drop_duplicates(
            subset=[
                "ID",
                "CLIENTE"
            ]
        )

    df_cliente["DATA_DISPUTA"] = pd.to_datetime(
        df_cliente["DATA_DISPUTA"],
        errors="coerce"
    ).dt.strftime("%d/%m/%Y")

    df_cliente["VALOR_ESTIMADO"] = df_cliente[
    "VALOR_ESTIMADO"
].apply(tratar_valor)

    df_cliente.to_excel(
        caminho,
        index=False
    )

    formatar_planilha(
        caminho
    )

    print(
        f"Dataset de {cliente} salvo em: {caminho}"
    )


def atualizar_datasets_clientes():
    """
    Atualiza a formatação dos datasets de clientes existentes.
    """

    for arquivo in PASTA_CLIENTES.glob("*.xlsx"):

        print(
            f"Atualizando: {arquivo.name}"
        )

        df = pd.read_excel(
            arquivo
        )

        if "DATA_DISPUTA" in df.columns:

            df["DATA_DISPUTA"] = pd.to_datetime(
                df["DATA_DISPUTA"],
                errors="coerce"
            ).dt.strftime("%d/%m/%Y")

        if "VALOR_ESTIMADO" in df.columns:

            df["VALOR_ESTIMADO"] = df[
                "VALOR_ESTIMADO"
            ].apply(
                lambda x:
                    "Sigiloso"

                    if( pd.notna(x) 
                    
                    and x != "Sigiloso"
                    and float(x) == 0
            )
            else x
        )
            
                
        df.to_excel(
            arquivo,
            index=False
        )

        formatar_planilha(
            arquivo
        )

        print(
            f"Atualizado com sucesso: {arquivo.name}"
        )

if __name__=="__main__":
    atualizar_datasets_clientes()
 