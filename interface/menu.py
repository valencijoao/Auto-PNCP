from pathlib import Path
import shutil
import sys

from config.caminhos import DADOS
from util import banco


def _pausa():
    input("\nPressione Enter para continuar...")


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
        ("Situação", "situacao"), ("Link PNCP", "link_pncp"),
    ]
    for titulo, chave in campos:
        print(f"{titulo}: {dados.get(chave) or '—'}")
    clientes = banco.consultar_clientes_contratacao(dados["id_interno"])
    print(f"Clientes associados: {', '.join(clientes) if clientes else 'Nenhum'}")
    return True


def _consulta_contratacao():
    cnpj = input("CNPJ: ").strip()
    ano_txt = input("Ano: ").strip()
    seq_txt = input("Sequencial: ").strip()
    if not cnpj.isdigit() or len(cnpj) != 14:
        print("CNPJ inválido. Informe os 14 números.")
        return
    try:
        ano, sequencial = int(ano_txt), int(seq_txt)
        if ano < 1900 or sequencial < 0:
            raise ValueError
    except ValueError:
        print("Ano ou sequencial inválido.")
        return
    _mostrar_contratacao(banco.consultar_contratacao(cnpj, ano, sequencial))


def _gerenciar_clientes():
    dados = banco.consultar_contratacao(
        input("CNPJ: ").strip(), input("Ano: ").strip(), input("Sequencial: ").strip()
    )
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


def _configuracoes():
    while True:
        print("\nCONFIGURAÇÕES\n1 - Criar novo banco padrão\n2 - Utilizar banco existente\n3 - Fazer backup do banco\n0 - Voltar")
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
            print(f"Banco selecionado: {banco.ARQUIVO_BANCO}")
            return
        if opcao == "3":
            origem = banco.ARQUIVO_BANCO
            if not origem.is_file():
                print("O banco ainda não existe.")
                continue
            pasta = DADOS / "backups"
            pasta.mkdir(parents=True, exist_ok=True)
            destino = pasta / f"compras_backup_{__import__('datetime').datetime.now():%Y%m%d_%H%M%S}.db"
            shutil.copy2(origem, destino)
            print(f"Backup salvo em: {destino}")
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
              "4": _consultar_banco, "5": _gerar_excel, "6": _configuracoes}
    while True:
        print("\n====================================\n           AUTO PAINEL\n====================================")
        print("1 - Minerar novas contratações\n2 - Consultar contratação\n3 - Gerenciar clientes\n4 - Consultar banco\n5 - Gerar dataset Excel\n6 - Configurações\n7 - Sair")
        escolha = input("\nEscolha: ").strip()
        if escolha == "7":
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
