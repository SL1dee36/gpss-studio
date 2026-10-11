from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat, QFont

from app.consts import GPSS_KEYWORDS, GPSS_DIRECTIVES


class GPSSHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, theme="dark"):
        super().__init__(parent)
        self.theme = theme
        self.rules = []
        self._init_formats()
        self._build_rules()

    def set_theme(self, theme):
        self.theme = theme
        self._init_formats()
        self._build_rules()
        self.rehighlight()

    def _init_formats(self):
        if self.theme == "dark":
            color_kw = QColor("#bcdfff")
            color_dir = QColor("#d2a8ff")
            color_sna = QColor("#79c0ff")
            color_num = QColor("#ffa657")
            color_comment = QColor("#7a8c9e")
            color_str = QColor("#7ee787")
        else:
            color_kw = QColor("#0969da")
            color_dir = QColor("#8250df")
            color_sna = QColor("#0550ae")
            color_num = QColor("#b78103")
            color_comment = QColor("#6c757d")
            color_str = QColor("#1a7f37")

        self.fmt_keyword = QTextCharFormat()
        self.fmt_keyword.setForeground(color_kw)
        self.fmt_keyword.setFontWeight(QFont.Bold)

        self.fmt_directive = QTextCharFormat()
        self.fmt_directive.setForeground(color_dir)
        self.fmt_directive.setFontWeight(QFont.Bold)

        self.fmt_sna = QTextCharFormat()
        self.fmt_sna.setForeground(color_sna)

        self.fmt_number = QTextCharFormat()
        self.fmt_number.setForeground(color_num)

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(color_comment)
        self.fmt_comment.setFontItalic(True)

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(color_str)

    def _build_rules(self):
        self.rules = []

        for kw in GPSS_KEYWORDS:
            pattern = QRegularExpression(rf"\b{kw}\b", QRegularExpression.CaseInsensitiveOption)
            self.rules.append((pattern, self.fmt_keyword))

        for d in GPSS_DIRECTIVES:
            pattern = QRegularExpression(rf"\b{d}\b", QRegularExpression.CaseInsensitiveOption)
            self.rules.append((pattern, self.fmt_directive))

        sna_patterns = [
            r"\b[QqFfSsVvXx](?:A|C|M|T|X|R)?\$[A-Za-z0-9_#]+",
            r"\bFN\$[A-Za-z0-9_#]+",
            r"\b(?:RN[1-7]|C1|AC1|PR|M1|CA|W)\b"
        ]
        for sna in sna_patterns:
            self.rules.append((QRegularExpression(sna, QRegularExpression.CaseInsensitiveOption), self.fmt_sna))

        self.rules.append((QRegularExpression(r"\b\d+(?:\.\d+)?\b"), self.fmt_number))
        self.rules.append((QRegularExpression(r'"[^"\\]*(?:\\.[^"\\]*)*"'), self.fmt_string))
        self.rules.append((QRegularExpression(r"'[^'\\]*(?:\\.[^'\\]*)*'"), self.fmt_string))
        self.rules.append((QRegularExpression(r";[^\n]*"), self.fmt_comment))

    def highlightBlock(self, text):
        user_data = self.currentBlockUserData()
        if user_data and hasattr(user_data, "label") and user_data.label.strip().startswith("*"):
            self.setFormat(0, len(text), self.fmt_comment)
            return

        if text.strip().startswith("*"):
            self.setFormat(0, len(text), self.fmt_comment)
            return

        for pattern, fmt in self.rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
