import os
import re
import pandas as pd
from excel.formatacao import formatar_planilha


# ===========================================
# CONFIGURAÇÕES
# ===========================================

arquivo = r"C:\Users\tec01\Desktop\pasta_de_trabalho\auto_painel\processos_atualizados.xlsx"

pasta_saida = "clientes"

os.makedirs(pasta_saida, exist_ok=True)

# ===========================================
# LÊ A PLANILHA
# ===========================================

df = pd.read_excel(
    arquivo
)

# Remove clientes vazios
clientes = (
    df["CLIENTE"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

print(f"Foram encontrados {len(clientes)} clientes.")

# ===========================================
# GERA UMA PLANILHA PARA CADA CLIENTE
# ===========================================

for cliente in clientes:

    df_cliente = df[
        df["CLIENTE"].astype(str).str.strip() == cliente
    ]

    # Remove caracteres inválidos para nome de arquivo
    nome_arquivo = re.sub(r'[\\/*?:"<>|]', "_", cliente)

    caminho_saida = os.path.join(
        pasta_saida,
        f"{nome_arquivo}.xlsx"
    )

    df_cliente.to_excel(
        caminho_saida,
        index=False
    )

    formatar_planilha(caminho_saida)

    print(f"Criado: {nome_arquivo}.xlsx")

print("\nConcluído!")