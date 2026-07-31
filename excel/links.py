import pandas as pd

def preencher_se_vazio(df,index,coluna,novo_valor):
    """
    Estabelece as condições para preenchimento de uma célula no Excel.
    """

    valor_atual = df.at[index, coluna]

    if novo_valor not in (None, "", "Não informado"):
        df.at[index,coluna] = novo_valor

    elif pd.isna(valor_atual) or str(valor_atual).strip() == "":
        df.at[index, coluna] = "Não informado"