"""Cadastro de contratações que não estão disponíveis no PNCP."""

from datetime import datetime
import math

from config.caminhos import COMPRAS
from ferramentas.gerar_dataset import (
    filtrar_novas_contratacoes,
    gerar_dataset,
    gerar_dataset_cliente,
    gerar_id_interno,
    salvar_dataset_cliente,
)
from util import banco
from util.cache import salvar_compra


def _data_iso(valor, campo, obrigatoria=False):
    texto = str(valor or "").strip()
    if not texto:
        if obrigatoria:
            raise ValueError(f"Informe a {campo}.")
        return None

    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).isoformat()
    except ValueError:
        pass

    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date().isoformat()
        except ValueError:
            continue

    raise ValueError(f"Data inválida para {campo}. Use DD/MM/AAAA ou AAAA-MM-DD.")


def _valor_decimal(valor, campo):
    texto = str(valor or "").strip().replace("R$", "").replace(" ", "")
    if not texto:
        return None
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        resultado = float(texto)
    except ValueError as erro:
        raise ValueError(f"Valor inválido para {campo}.") from erro
    if not math.isfinite(resultado) or resultado < 0:
        raise ValueError(f"O valor de {campo} não pode ser negativo.")
    return resultado


def cadastrar_contratacao_manual(cnpj, ano, sequencial, formulario):
    """Salva os dados no formato JSON existente, registra no SQLite e atualiza clientes."""
    cnpj = "".join(caractere for caractere in str(cnpj) if caractere.isdigit())
    if len(cnpj) != 14:
        raise ValueError("CNPJ inválido. Informe os 14 números.")

    try:
        ano = int(ano)
        sequencial = int(sequencial)
    except (TypeError, ValueError) as erro:
        raise ValueError("Ano e sequencial devem ser numéricos.") from erro
    if ano < 1900 or sequencial < 1:
        raise ValueError("Ano ou sequencial inválido.")

    orgao = str(formulario.get("orgao") or "").strip()
    portal = str(formulario.get("portal") or "").strip()
    if not orgao:
        raise ValueError("Informe o órgão.")
    if not portal:
        raise ValueError("Informe o nome do portal.")

    clientes = list(dict.fromkeys(
        str(cliente).strip()
        for cliente in formulario.get("clientes", [])
        if str(cliente).strip()
    ))
    numero_compra = str(formulario.get("numero_compra") or sequencial).strip()
    data_publicacao = _data_iso(
        formulario.get("data_publicacao"), "data de publicação", obrigatoria=True
    )
    data_disputa = _data_iso(formulario.get("data_disputa"), "data da disputa")
    valor_estimado = _valor_decimal(formulario.get("valor_estimado"), "valor estimado")
    valor_homologado = _valor_decimal(formulario.get("valor_homologado"), "valor homologado")

    existente = banco.consultar_contratacao(cnpj, ano, sequencial)
    if existente:
        raise ValueError("Já existe uma contratação cadastrada com esse CNPJ/ANO/SEQUENCIAL.")

    pasta = COMPRAS / f"{cnpj}-{ano}-{sequencial}"
    if pasta.exists() and any(pasta.iterdir()):
        raise ValueError("Já existem arquivos para esse CNPJ/ANO/SEQUENCIAL na pasta de compras.")

    dados = {
        "orgaoEntidade": {
            "cnpj": cnpj,
            "razaoSocial": orgao,
            "esferaId": str(formulario.get("esfera") or "").strip() or None,
        },
        "unidadeOrgao": {
            "ufSigla": str(formulario.get("estado") or "").strip().upper() or None,
            "nomeUnidade": str(formulario.get("unidade") or "").strip() or None,
            "municipioNome": str(formulario.get("municipio") or "").strip() or None,
        },
        "numeroCompra": numero_compra,
        "anoCompra": ano,
        "sequencialCompra": sequencial,
        "valorTotalEstimado": valor_estimado,
        "valorTotalHomologado": valor_homologado,
        "dataPublicacaoPncp": data_publicacao,
        "dataEncerramentoProposta": data_disputa,
        "modalidadeNome": str(formulario.get("modalidade") or "").strip() or None,
        "modoDisputaNome": str(formulario.get("modo_disputa") or "").strip() or None,
        "situacaoCompraNome": str(formulario.get("situacao") or "").strip() or None,
        "srp": bool(formulario.get("srp", False)),
        "linkSistemaOrigem": str(formulario.get("link_portal") or "").strip() or None,
        "_origemManual": portal,
        "_linkPNCPManual": "",
    }
    item = str(formulario.get("item") or "").strip()
    compra = {"dados": dados, "itens": [], "clientes": clientes}
    id_interno = gerar_id_interno(cnpj, ano, sequencial, portal)

    # Mantém os JSONs por contratação no formato que o minerador e o dataset já leem.
    salvar_compra(cnpj, ano, sequencial, "dados", dados)
    salvar_compra(cnpj, ano, sequencial, "itens", [])
    salvar_compra(
        cnpj, ano, sequencial, "clientes", {"clientes": clientes, "item": item}
    )
    banco.inserir_compra(compra)

    atualizados = []
    falhas = {}
    if clientes:
        try:
            df = gerar_dataset()
            df_novas = filtrar_novas_contratacoes(df, [id_interno])
            for cliente in clientes:
                try:
                    df_cliente = gerar_dataset_cliente(df_novas, cliente)
                    salvar_dataset_cliente(df_cliente, cliente)
                    atualizados.append(cliente)
                except Exception as erro:
                    falhas[cliente] = str(erro)
        except Exception as erro:
            falhas = {cliente: str(erro) for cliente in clientes}

    return {
        "id_interno": id_interno,
        "clientes_atualizados": atualizados,
        "falhas": falhas,
    }
