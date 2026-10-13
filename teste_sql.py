from util.banco import conectar

conn = conectar()

itens = conn.execute("""
    SELECT    
        COUNT(*) AS TOTAL_ITENS,
        COUNT(DISTINCT id_interno) AS CONTRATACOES_COM_ITENS
    FROM itens;
""").fetchone()

print("Total de itens:", itens[0])
print("Contratação com itens:", itens[1])


conn.close()



