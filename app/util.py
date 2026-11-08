from PySide6.QtGui import QFont


def get_monospace_font(size=10, bold=False):
    font = QFont()
    font.setFamilies(["Consolas", "DejaVu Sans Mono", "Liberation Mono", "Noto Sans Mono", "Ubuntu Mono", "Courier New", "monospace"])
    font.setPointSize(size)
    if bold:
        font.setBold(True)
    font.setStyleHint(QFont.Monospace)
    font.setFixedPitch(True)
    return font


def get_ui_font(size=9, bold=False, italic=False):
    font = QFont()
    font.setFamilies(["Segoe UI", "Ubuntu", "Cantarell", "DejaVu Sans", "Liberation Sans", "Noto Sans", "sans-serif"])
    font.setPointSize(size)
    if bold:
        font.setBold(True)
    if italic:
        font.setItalic(True)
    return font


def filter_table(table, text):
    text = text.lower().strip()
    for r in range(table.rowCount()):
        if not text:
            table.setRowHidden(r, False)
            continue
        match = False
        for c in range(table.columnCount()):
            it = table.item(r, c)
            if it and text in it.text().lower():
                match = True
                break
        table.setRowHidden(r, not match)
