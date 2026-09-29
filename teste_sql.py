from ferramentas.gerar_orgaos import gerar_orgaos 
from ferramentas.gerar_dataset import gerar_dataset
from util.banco import inserir_orgaos, inserir_contratacoes, inserir_vinculos_clientes, inserir_clientes
import sqlite3

df = gerar_dataset()

inserir_contratacoes(df)
inserir_clientes(df)
inserir_vinculos_clientes(df)

conn = sqlite3.connect("dados/banco/compras.db")

cursor = conn.cursor()

cursor.execute("""
    SELECT
        o.estado,
        COUNT(c.id_interno)
    FROM contratacoes c
    JOIN orgaos o
        ON c.cnpj = o.cnpj
    GROUP BY o.estado
    ORDER BY COUNT(c.id_interno) DESC
""")

for estado, quantidade in cursor.fetchall():
    print(estado, quantidade)

cursor.execute("""
    SELECT
        COUNT(*) AS total_linhas,
        COUNT(DISTINCT c.id_interno) AS contratacoes_unicas
    FROM contratacoes c
    JOIN orgaos o
        ON c.cnpj = o.cnpj
""")

print(cursor.fetchone())

conn.close()