from pathlib import Path
import shutil
import sys
from datetime import datetime

from config.caminhos import DADOS
from util import banco


def _pausa():
    input("\nPressione Enter para continuar...")


def _solicitar_identificador_contratacao():
    """Lê a identificação no mesmo formato usado pela mineração."""
    entrada = input("CNPJ/ANO/SEQUENCIAL: ").strip()
    partes = [parte.strip() for parte in entrada.split("/")]
    if (
        len(partes) != 3
        or len(partes[0]) != 14
        or not partes[0].isdigit()
        or len(partes[1]) != 4
        or not partes[1].isdigit()
        or not partes[2].isdigit()
    ):
        print("Formato inválido. Use CNPJ/ANO/SEQUENCIAL, por exemplo: 12345678000190/2026/12.")
        return None

    ano, sequencial = int(partes[1]), int(partes[2])
    if ano < 1900 or sequencial < 1:
        print("Ano ou sequencial inválido.")
        return None
    return partes[0], ano, sequencial


def _mostrar_contratacao(dados):
    if not dados:
        print("Contratação não encontrada.")
        return False
    campos = [
        ("ID interno", "id_interno"), ("ID", "id"),
        ("Número da compra", "numero_compra"), ("Ano", "ano_compra"),
        ("Sequencial", "sequencial_compra"), ("CNPJ", "cnpj"),
        ("Órgão", "orgao"), ("Estado", "estado"),
        ("Município", "municipio"), ("Valor estimado", "valor_estimado"),
        ("Data de envio", "data_envio"),
        ("Situação", "situacao"), ("Link PNCP", "link_pncp"),
        ("Link do portal", "link_portal"),
    ]
    for titulo, chave in campos:
        print(f"{titulo}: {dados.get(chave) or '—'}")
    clientes = banco.consultar_clientes_contratacao(dados["id_interno"])
    print(f"Clientes associados: {', '.join(clientes) if clientes else 'Nenhum'}")
    return True


def _consulta_contratacao():
    identificador = _solicitar_identificador_contratacao()
    if identificador is None:
        return
    cnpj, ano, sequencial = identificador
    _mostrar_contratacao(banco.consultar_contratacao(cnpj, ano, sequencial))


def _gerenciar_clientes():
    identificador = _solicitar_identificador_contratacao()
    if identificador is None:
        return
    dados = banco.consultar_contratacao(*identificador)
    if not _mostrar_contratacao(dados):
        return
    id_interno = dados["id_interno"]
    while True:
        clientes = banco.consultar_clientes_contratacao(id_interno)
        print("\nClientes associados:")
        print("\n".join(f"- {c}" for c in clientes) if clientes else "Nenhum cliente associado.")
        print("1 - Adicionar cliente\n2 - Remover cliente\n0 - Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            return
        if opcao not in {"1", "2"}:
            print("Opção inválida.")
            continue
        cliente = input("Nome do cliente: ").strip()
        if not cliente:
            print("O nome do cliente não pode ficar vazio.")
            continue
        acao = "adicionar" if opcao == "1" else "remover"
        if input(f"Confirma {acao} '{cliente}'? (s/n): ").strip().lower() != "s":
            continue
        if opcao == "1":
            banco.adicionar_cliente_contratacao(id_interno, cliente)
        else:
            banco.remover_cliente_contratacao(id_interno, cliente)


def _adicionar_contratacao_manual():
    from ferramentas.contratacao_manual import cadastrar_contratacao_manual

    identificador = _solicitar_identificador_contratacao()
    if identificador is None:
        return
    cnpj, ano, sequencial = identificador

    print("\nDados da contratação manual. Órgão, portal e data de publicação são obrigatórios.")
    formulario = {
        "numero_compra": input("Número da compra/processo [usa o sequencial]: ").strip(),
        "orgao": input("Órgão: ").strip(),
        "estado": input("Estado (UF): ").strip(),
        "municipio": input("Município: ").strip(),
        "unidade": input("Unidade: ").strip(),
        "esfera": input("Esfera do órgão: ").strip(),
        "portal": input("Nome do portal: ").strip(),
        "link_portal": input("Link da contratação no portal: ").strip(),
        "data_publicacao": input("Data de publicação (DD/MM/AAAA ou AAAA-MM-DD): ").strip(),
        "data_disputa": input("Data da disputa (opcional): ").strip(),
        "modalidade": input("Modalidade: ").strip(),
        "modo_disputa": input("Modo de disputa: ").strip(),
        "situacao": input("Situação: ").strip(),
        "valor_estimado": input("Valor estimado (opcional): ").strip(),
        "valor_homologado": input("Valor homologado (opcional): ").strip(),
        "item": input("Item/objeto destinado ao cliente: ").strip(),
    }
    formulario["clientes"] = [
        cliente.strip()
        for cliente in input("Clientes associados, separados por vírgula (opcional): ").split(",")
        if cliente.strip()
    ]
    formulario["srp"] = input("É registro de preços? (s/n; Enter = não): ").strip().lower() in {"s", "sim"}

    print(f"\nContratação: {cnpj}/{ano}/{sequencial}")
    print(f"Órgão: {formulario['orgao'] or '—'} | Portal: {formulario['portal'] or '—'}")
    print(f"Clientes: {', '.join(formulario['clientes']) or 'Nenhum'}")
    if input("Confirmar o cadastro? (s/n): ").strip().lower() not in {"s", "sim"}:
        print("Cadastro cancelado.")
        return

    resultado = cadastrar_contratacao_manual(cnpj, ano, sequencial, formulario)
    print(f"Contratação cadastrada: {resultado['id_interno']}")
    if resultado["clientes_atualizados"]:
        print(f"Planilhas atualizadas: {', '.join(resultado['clientes_atualizados'])}")
    elif formulario["clientes"]:
        print("Contratação cadastrada, mas não foi possível atualizar as planilhas dos clientes.")
    for cliente, erro in resultado["falhas"].items():
        print(f"Falha na planilha de {cliente}: {erro}")


def _consultar_banco():
    filtros = {"1": ("estado", "Estado"), "2": ("orgao", "Órgão"),
               "3": ("cliente", "Cliente"), "4": ("situacao", "Situação")}
    print("1 - Estado\n2 - Órgão\n3 - Cliente\n4 - Situação")
    escolha = input("Filtro: ").strip()
    if escolha not in filtros:
        print("Opção inválida.")
        return
    chave, rotulo = filtros[escolha]
    resultados = banco.consultar_contratacoes_filtro(chave, input(f"{rotulo}: ").strip())
    if not resultados:
        print("Nenhuma contratação encontrada.")
        return
    print(f"\n{len(resultados)} resultado(s):")
    for item in resultados:
        print(f"{item.get('id_interno')} | {item.get('id') or '—'} | {item.get('orgao') or '—'} | {item.get('estado') or '—'} | {item.get('situacao') or '—'}")


def _gerar_excel():
    from ferramentas.gerar_dataset import gerar_dataset
    df = gerar_dataset()
    if df.empty:
        print("Não há dados disponíveis para exportar.")
        return
    filtros = input("Filtro opcional (estado, cliente ou ano; Enter para todos): ").strip()
    if filtros:
        tipo, sep, valor = filtros.partition("=")
        tipo, valor = tipo.strip().lower(), valor.strip()
        colunas = {"estado": "ESTADO", "cliente": "CLIENTE", "ano": "ANO_COMPRA"}
        if not sep or tipo not in colunas or not valor:
            print("Formato inválido. Use estado=SP, cliente=Nome ou ano=2026.")
            return
        coluna = colunas[tipo]
        if coluna not in df.columns:
            print(f"Não há a coluna {coluna} nos dados disponíveis.")
            return
        if tipo == "ano":
            try:
                df = df[df[coluna].astype(str) == str(int(valor))]
            except ValueError:
                print("Ano inválido.")
                return
        else:
            df = df[df[coluna].astype(str).str.contains(valor, case=False, na=False)]
    if df.empty:
        print("Nenhum registro corresponde ao filtro.")
        return
    sugestao = DADOS / "datasets" / "dataset_exportado.xlsx"
    destino = input(f"Arquivo Excel de destino [{sugestao}]: ").strip()
    caminho = Path(destino).expanduser() if destino else sugestao
    if caminho.suffix.lower() != ".xlsx":
        caminho = caminho.with_suffix(".xlsx")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(caminho, index=False)
    print(f"Excel gerado com {len(df)} registro(s): {caminho.resolve()}")


def _criar_backup_banco():
    origem = banco.ARQUIVO_BANCO
    if not origem.is_file():
        raise FileNotFoundError("O banco selecionado ainda não existe.")
    pasta = DADOS / "backups"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{origem.stem}_backup_{datetime.now():%Y%m%d_%H%M%S_%f}.db"
    shutil.copy2(origem, destino)
    return destino


def _configuracoes():
    while True:
        print("\nCONFIGURAÇÕES\n1 - Criar novo banco padrão\n2 - Utilizar banco existente\n3 - Fazer backup do banco\n4 - Mesclar backup no banco selecionado\n0 - Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            return
        if opcao == "1":
            banco.definir_banco(DADOS / "banco" / "compras.db")
            banco.criar_banco()
            return
        if opcao == "2":
            caminho = Path(input("Caminho do arquivo .db: ").strip().strip('"')).expanduser()
            if not caminho.is_file() or caminho.suffix.lower() != ".db":
                print("Arquivo .db não encontrado.")
                continue
            banco.definir_banco(caminho)
            banco.criar_banco()
            print(f"Banco selecionado: {banco.ARQUIVO_BANCO}")
            return
        if opcao == "3":
            destino = _criar_backup_banco()
            print(f"Backup salvo em: {destino}")
            continue
        if opcao == "4":
            print(f"Banco de destino: {banco.ARQUIVO_BANCO}")
            caminho = Path(input("Caminho do backup .db: ").strip().strip('"')).expanduser().resolve()
            if not caminho.is_file() or caminho.suffix.lower() != ".db":
                print("Arquivo de backup .db não encontrado.")
                continue
            if caminho == banco.ARQUIVO_BANCO.resolve():
                print("Selecione um arquivo diferente do banco de destino.")
                continue
            print("Os registros ausentes serão adicionados. Em caso de conflito, os dados do banco de destino serão mantidos.")
            if input("Fazer uma cópia de segurança do destino e continuar? (s/n): ").strip().lower() != "s":
                continue
            backup_destino = _criar_backup_banco()
            adicionados = banco.mesclar_banco(caminho)
            print(f"Cópia de segurança do destino: {backup_destino}")
            print("Registros adicionados:")
            for tabela, quantidade in adicionados.items():
                print(f"- {tabela}: {quantidade}")
            continue
        print("Opção inválida.")


def _minerar():
    from ferramentas.minerador_compras import (
        atualizar_datasets_mineracao,
        baixar_compras,
    )
    print("Informe uma ou mais contratações no formato CNPJ/ANO/SEQUENCIAL, separadas por vírgula.")
    entrada = input("Contratações: ").strip()
    contratacoes = [parte.strip() for parte in entrada.split(",") if parte.strip()]
    if not contratacoes:
        print("Nenhuma contratação informada.")
        return
    baixadas = []
    baixar_compras(contratacoes, baixadas)
    atualizar_datasets_mineracao(baixadas)
    print(f"Processamento concluído. Contratações baixadas: {len(baixadas)}")


def _inicializar_banco():
    if banco.ARQUIVO_BANCO.exists():
        try:
            banco.criar_banco()
        except Exception as erro:
            print(f"Não foi possível abrir o banco configurado: {erro}")
            return False
        return True
    print(f"Banco padrão não encontrado: {banco.ARQUIVO_BANCO}")
    if input("Criar um novo banco padrão? (s/n): ").strip().lower() == "s":
        banco.criar_banco()
        return True
    print("Escolha 'Configurações' para selecionar um banco existente.")
    return False


def main():
    if not _inicializar_banco():
        # Permite entrar em configurações sem abrir banco.
        opcao = input("Abrir configurações agora? (s/n): ").strip().lower()
        if opcao == "s":
            _configuracoes()
        if not banco.ARQUIVO_BANCO.exists():
            return
    opcoes = {"1": _minerar, "2": _consulta_contratacao, "3": _gerenciar_clientes,
              "4": _consultar_banco, "5": _gerar_excel, "6": _configuracoes,
              "7": _adicionar_contratacao_manual}
    while True:
        print("\n====================================\n           AUTO PAINEL\n====================================")
        print("1 - Minerar novas contratações\n2 - Consultar contratação\n3 - Gerenciar clientes\n4 - Consultar banco\n5 - Gerar dataset Excel\n6 - Configurações\n7 - Adicionar contratação manualmente\n8 - Sair")
        escolha = input("\nEscolha: ").strip()
        if escolha == "8":
            print("Até logo.")
            return
        acao = opcoes.get(escolha)
        if acao is None:
            print("Opção inválida.")
        else:
            try:
                acao()
            except KeyboardInterrupt:
                print("\nOperação cancelada.")
            except Exception as erro:
                print(f"Não foi possível concluir a operação: {erro}")
        _pausa()


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nAutoPainel encerrado.")
        sys.exit(0)
