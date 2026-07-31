from api.session import criar_sessao
from excel.formatacao import formatar_planilha
from requests.exceptions import Timeout, RequestException


PASTA_SAIDA = r"C:\Users\tec01\Desktop\painel_tecsystems\enviadas"
ARQUIVO_SAIDA = "processos_atualizados.xlsx"
arquivo_original = r"C:\Users\tec01\Desktop\painel_tecsystems\template_painel.xlsx"

import re
import time
import pandas as pd

from api.session import criar_sessao
from util.portais import (
    identificar_portal,
    listar_desconhecidos   )
from excel.formatacao import formatar_planilha
from excel.datas import formatar_data

session = criar_sessao()

df = pd.read_excel(
    arquivo_original,
    skiprows=2
)


colunas_texto = [
    "ID",
    "ORGÃO",
    "DATA DA DISPUTA",
    "PORTAL",
    "LINK PORTAL"
]

for coluna in colunas_texto:
    df[coluna] = df[coluna].astype("object")   

print("Inciando processamento...")

for index in df.index:

    print(f"Processando linha {index + 4}")

    link = str(df.at[index,'LINK PNCP']).strip()

    if not link or "pncp.gov.br" not in link:
        continue
    
    try:

        padrao = r'editais/(\d+)/(\d+)/(\d+)'
        resultado = re.search(padrao, link)

        if not resultado:
            continue

        cnpj, ano, sequencial = resultado.groups()

        url_api = (
            f"https://pncp.gov.br/api/consulta/v1/orgaos/"
            f"{cnpj}/compras/{ano}/{sequencial}"
        ) 


        resposta = session.get(
                url_api,
                timeout=120
            )
                

        if resposta.status_code != 200:
            continue


        print("Status:", resposta.status_code)

        dados = resposta.json()

        numero_compra = dados.get('numeroCompra')
        
        ano_compra = dados.get('anoCompra')
        if numero_compra and ano_compra:
            id_processo = f"{numero_compra}/{ano_compra}"
        else:
            id_processo = None 
        
        valor = dados.get('valorTotalEstimado')
        if valor is None:
            valor_total = None
        elif float(valor) == 0:
            valor_total = "Sigiloso"
        else:
            valor_total = float(valor)

        orgao = dados.get('orgaoEntidade', {}).get('razaoSocial')
        esfera = dados.get('orgaoEntidade', {}).get('esferaId')
        srp = dados.get('srp')
        
        data_disputa = formatar_data(   
            dados.get('dataEncerramentoProposta')
                                     )
        
        link_portal = dados.get('linkSistemaOrigem')
        portal = identificar_portal(link_portal)

        df.at[index, 'ID'] = id_processo
        df.at[index, 'VALOR'] = valor_total
        df.at[index, 'ORGÃO'] = orgao
        df.at[index, 'DATA DA DISPUTA'] = data_disputa
        df.at[index, 'PORTAL'] = portal
        df.at[index, 'LINK PORTAL'] = link_portal

        estado = dados.get('unidadeOrgao',{}).get('ufSigla')
        municipio = dados.get('unidadeOrgao',{}).get('municipioNome')

        print(f"Linha {index + 4} preenchida com sucesso.")


        
        time.sleep(3)
    
    except Exception as e:
        print(f"Erro na linha {index + 4}: {e}")

df.to_excel(
        ARQUIVO_SAIDA,
        index=False
        )
 

formatar_planilha(ARQUIVO_SAIDA)

listar_desconhecidos()

print('\nConcluído!')






