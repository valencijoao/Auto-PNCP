from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

def formatar_planilha(arquivo_saida):
    """
    Aplica toda a formatação na planilha de output.
    """
    wb = load_workbook(arquivo_saida)
    ws = wb.active

    # ===============================
    # Cabeçalho
    # ===============================

    azul = PatternFill(
        fill_type="solid",
        fgColor="1F4E78"
    )

    fonte = Font(
        color="FFFFFF",
        bold=True
    )

    for celula in ws[1]:
        celula.fill = azul
        celula.font = fonte
        celula.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # ===============================
    # Congela primeira linha
    # ===============================

    ws.freeze_panes = "A2"

    # ===============================
    # Filtro
    # ===============================

    ws.auto_filter.ref = ws.dimensions

    # ===============================
    # Ajusta largura automaticamente
    # ===============================

    for coluna in ws.columns:

        letra = get_column_letter(coluna[0].column)

        maior = 0

        for celula in coluna:

            if celula.value is not None:
                maior = max(
                    maior,
                    len(str(celula.value))
                )

        ws.column_dimensions[letra].width = min(maior + 4, 60)

    # ===============================
    # Descobre colunas
    # ===============================

    coluna_valor = None

    for celula in ws[1]:

        texto = str(celula.value).strip().upper()

        if texto == "VALOR":
            coluna_valor = celula.column

    # ===============================
    # Formata moeda
    # ===============================

    if coluna_valor:

        for linha in range(2, ws.max_row + 1):

            c = ws.cell(
                row=linha,
                column=coluna_valor
            )

            if isinstance(c.value, (int, float)):
                c.number_format = '[$R$-416] #,##0.00'

    # ===============================
    # Alinhamento
    # ===============================

    for linha in ws.iter_rows():

        for celula in linha:

            celula.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

    wb.save(arquivo_saida)



    