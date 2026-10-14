"""Exportaciones en memoria; no se envían los resultados a servicios externos."""
from io import BytesIO
import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE


def to_csv(data):
    return data.to_csv(index=False, lineterminator="\n").encode("utf-8-sig")


def to_excel(data):
    output = BytesIO()
    headers = list(data.columns)
    header_rows = list(zip(*headers)) if isinstance(data.columns, pd.MultiIndex) else [headers]
    if len(data) + len(header_rows) > 1_048_576 or len(headers) > 16_384:
        raise ValueError("Los datos superan los límites de Excel. Exporta a CSV.")
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Escribir cada celda como texto conserva ceros iniciales y fórmulas literales.
        pd.DataFrame().to_excel(writer, sheet_name="Datos", index=False)
        sheet = writer.sheets["Datos"]
        for row_index, row in enumerate([*header_rows, *data.itertuples(index=False, name=None)], 1):
            for col_index, value in enumerate(row, 1):
                if value is not None and len(str(value)) > 32767:
                    raise ValueError("Una celda supera 32.767 caracteres; usa CSV para evitar truncarla.")
                if isinstance(value, str) and ILLEGAL_CHARACTERS_RE.search(value):
                    raise ValueError("Una celda contiene caracteres no admitidos por Excel; usa CSV para conservarlos.")
                cell = sheet.cell(row_index, col_index, value)
                if isinstance(value, str):
                    cell.data_type = "s"
    return output.getvalue()
