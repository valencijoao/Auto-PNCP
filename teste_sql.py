from ferramentas.gerar_orgaos import gerar_orgaos 
from ferramentas.gerar_dataset import gerar_dataset
from util.banco import inserir_orgaos, inserir_contratacoes
import sqlite3

df = gerar_dataset()

inserir_contratacoes(df)

conn = sqlite3.connect("dados/banco/compras.db")

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM contratacoes")

print(cursor.fetchone()[0])

conn.close()
