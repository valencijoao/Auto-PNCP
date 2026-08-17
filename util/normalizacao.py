import json
import pandas as pd


from config.caminhos import CAMINHO_DOMINIOS, CAMINHO_ORGAOS
from ferramentas.gerar_dominios import carregar_dominios
from util.portais import traduzir_portal 


DOMINIOS = carregar_dominios()
ORGAOS = CAMINHO_ORGAOS
with open(
    ORGAOS,
    encoding="utf-8"
) as arquivo:
    ORGAO = json.load(
        arquivo
    )


def normalizar_texto(valor):
    """
    Normaliza espaços e caracteres invisíveis de um texto.
    """

    if pd.isna(valor):
        return valor

    valor = str(valor)

    valor = valor.replace( 
        "\xa0",
        " "
    )

    valor = " ".join(
        valor.split()
    )

    return valor.strip()


def normalizar_data(valor):
    """
    Converte as datas para o tipo datetime.
    """

    if pd.isna(valor):
        return pd.NaT

    return pd.to_datetime(
        valor,
        errors="coerce"
    )


def normalizar_valores(valor):
    """
    Converte monetário para numérico.
    """

    if pd.isna(valor):
        return pd.NA

    if isinstance(valor, str):

        valor = valor.strip()

        if valor.lower() == "sigiloso":
            return pd.NA

        valor = valor.replace(
            ".",
            ""
        )

        valor = valor.replace(
            ",",
            "."
        )

    try:
        return float(valor)

    except (ValueError, TypeError):
        return pd.NA

def normalizar_cnpj(valor):
    """
    Normaliza unicamente os CNPJ de orgãos ou forncedores, mantendo somente números.
    """

    if pd.isna(valor):
        return valor

    valor = str(valor)

    return "".join(
        caractere
        for caractere in valor
        if caractere.isdigit() 
    )


def normalizar_dominio(valor, dominio):
    """
    Traduz um código utilizando um termo cadastrado como domínio.
    """

    if pd.isna(valor):
        return valor

    dominio = DOMINIOS.get(
        dominio,
        {}
    )

    chave = str(valor)

    return dominio.get(
        chave,
        valor
    )


def normalizar_orgao(df):
    """
    Padroniza os dados do órgão utilizando o CNPJ
    como chave de relacionamento.
    """

    if "CNPJ" in df.columns:
        return df

    for indice, linha in df.iterrows():

        cnpj = linha["CNPJ"]

        if pd.isna(cnpj):
            continue

        cnpj = str(cnpj)

        dados_orgao = ORGAO.get(
            cnpj
        )

        if not dados_orgao:
            continue

        if dados_orgao.get("RAZAO_SOCIAL"):
            df.at[
                indice,
                "ORGAO",
            ] = dados_orgao[
                "UF"
            ]

        if dados_orgao.get("MUNICIPIO"):
            df.at[
                indice,
                "MUNICIPIO"
            ] = dados_orgao[
                "MUNICIPIO"
            ]

        if dados_orgao.get("UNIDADE"):
            df.at[
                indice,
                "UNIDADE"
            ] = dados_orgao[
                "UNIDADE"
            ]

    return df

def normalizar_portal(valor):
    """
    Normaliza o portal utilizando as regras
    existentes em util.portais.
    """

    if pd.isna(valor):
        return valor

    valor = str(valor).strip()

    if not valor:
        return valor

    return traduzir_portal(
        valor
    )


def normalizar_dataset(df):
    """
    Aplica formatações no DataFrame bruto.
    """

    colunas_texto =  [
        "CLIENTE",
        "ORGAO",
        "ESTADO",
        "UNIDADE",
        "MUNICIPIO",
        "MODALIDADE",
        "MODO_DISPUTA",
        "SITUACAO"
    ]

    for coluna in colunas_texto:

        if coluna in df.columns:

            df[coluna] = df[coluna].apply(
                normalizar_texto,
            )

    if "CNPJ" in df.columns:

        df["CNPJ"] = df["CNPJ"].apply(
            normalizar_cnpj
        )


    colunas_data = [
        "DATA_DISPUTA",
        "DATA_PUBLICACAO"
    ]

    for coluna in colunas_data:

        if coluna in df.columns:

            df[coluna] = df[coluna].apply(
                normalizar_data
            )


    colunas_valor = [
        "VALOR_ESTIMADO",
        "VALOR HOMOLOGADO"
    ]

    for coluna in colunas_valor:

        if coluna in df.columns:

            df[coluna] = df[coluna].apply(
                normalizar_valores
            )

    if "MODALIDADE" in df.columns:

        df["MODALIDADE"] = df[
            "MODALIDADE"
        ].apply(
            lambda x: normalizar_dominio(
                x,
                "modalidade"
            )
        )

    if "MODO_DISPUTA" in df.columns:

        df["MODO_DISPUTA"] = df[
            "MODO_DISPUTA"
        ].apply(
            lambda x: normalizar_dominio(
                x,
                "modoDisputa"
            )
        )

    if "SITUACAO" in df.columns:

        df["SITUACAO"] = df[
            "SITUACAO"
        ].apply(
            lambda x: normalizar_dominio(
                x,
                "situacaoCompra"
            )
        )

    if "PORTAL" in df.columns:

        df["PORTAL"] = df[
            "PORTAL"
        ].apply(
            normalizar_portal
        )

    df = normalizar_orgao(df)

    return df


