from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton


class SearchBar(QFrame):
    def __init__(self, editor, parent=None, title="Поиск:", placeholder="Введите текст для поиска..."):
        super().__init__(parent)
        self.editor = editor
        self.setObjectName("search_bar")
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        lbl = QLabel(title)
        lbl.setObjectName("search_lbl_title")

        self.edit_find = QLineEdit()
        self.edit_find.setObjectName("search_edit")
        self.edit_find.setPlaceholderText(placeholder)
        self.edit_find.setFixedHeight(28)
        self.edit_find.returnPressed.connect(self.find_next)
        self.edit_find.textChanged.connect(self._on_text_changed)

        self.btn_prev = QPushButton("Назад")
        self.btn_prev.setObjectName("search_btn_prev")
        self.btn_prev.setFixedHeight(28)
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setFocusPolicy(Qt.NoFocus)
        self.btn_prev.clicked.connect(self.find_prev)

        self.btn_next = QPushButton("Далее")
        self.btn_next.setObjectName("search_btn_next")
        self.btn_next.setFixedHeight(28)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFocusPolicy(Qt.NoFocus)
        self.btn_next.clicked.connect(self.find_next)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("search_lbl_count")
        self.lbl_count.setAlignment(Qt.AlignCenter)

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.setObjectName("search_btn_close")
        self.btn_close.setFixedHeight(28)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFocusPolicy(Qt.NoFocus)
        self.btn_close.clicked.connect(self.hide_bar)

        layout.addWidget(lbl)
        layout.addWidget(self.edit_find, 1)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.lbl_count)
        layout.addWidget(self.btn_close)

        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide_bar()
            return
        super().keyPressEvent(event)

    def show_bar(self):
        self.show()
        selected = self.editor.textCursor().selectedText()
        if selected and "\n" not in selected:
            self.edit_find.setText(selected)
        self.edit_find.setFocus()
        self.edit_find.selectAll()

    def hide_bar(self):
        self.hide()
        self.editor.setFocus()

    def _on_text_changed(self, text):
        self._update_count(text)

    def find_next(self):
        text = self.edit_find.text()
        if not text:
            self.lbl_count.setText("")
            return
        found = self.editor.find(text)
        if not found:
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text)
        self._update_count(text)

    def find_prev(self):
        text = self.edit_find.text()
        if not text:
            self.lbl_count.setText("")
            return
        found = self.editor.find(text, QTextDocument.FindBackward)
        if not found:
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text, QTextDocument.FindBackward)
        self._update_count(text)

    def _update_count(self, text):
        if not text:
            self.lbl_count.setText("")
            return
        content = self.editor.toPlainText()
        total = content.lower().count(text.lower())
        if total == 0:
            self.lbl_count.setText("Не найдено")
        else:
            self.lbl_count.setText(f"Найдено: {total}")
