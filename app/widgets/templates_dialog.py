from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QTextEdit, QPushButton, QLabel, QSplitter
)

TEMPLATES = [
    {
        "title": "1. Одноканальная СМО (M/M/1)",
        "desc": "Классическая одноканальная система массового обслуживания с очередью. Поток заявок поступает к единственному прибору SERVER.",
        "code": """* МОДЕЛЬ: Одноканальная СМО (M/M/1)
* Поток заявок с интервалом 10 +/- 4 ед.
* Время обслуживания прибором SERVER: 8 +/- 3 ед.

  GENERATE 10,4         ; Поступление заявок
  QUEUE LINE            ; Вход в очередь ожидания
  SEIZE SERVER          ; Занятие обслуживающего прибора
  DEPART LINE           ; Выход из очереди
  ADVANCE 8,3           ; Обслуживание заявки
  RELEASE SERVER        ; Освобождение прибора
  TERMINATE 1           ; Учёт обслуженной заявки

  START 1000            ; Смоделировать 1000 заявок
  END
"""
    },
    {
        "title": "2. Многоканальная СМО (M/M/n - STORAGE)",
        "desc": "Многоканальная система с пулом параллельных идентичных каналов (STORAGE). Заявки ждут в общей очереди.",
        "code": """* МОДЕЛЬ: Многоканальная СМО (3 параллельных канала)
* Пул каналов обслуживания описан через накопитель STORAGE

CHANNELS STORAGE S(3)   ; Емкость накопителя: 3 прибора

  GENERATE 5,2          ; Интенсивный входящий поток
  QUEUE WAITING         ; Общая очередь к свободным каналам
  ENTER CHANNELS,1      ; Занятие одного свободного канала
  DEPART WAITING        ; Выход из очереди
  ADVANCE 12,4          ; Время обслуживания в канале
  LEAVE CHANNELS,1      ; Освобождение канала
  TERMINATE 1           ; Учет обслуженной заявки

  START 500             ; Смоделировать 500 заявок
  END
"""
    },
    {
        "title": "3. СМО с абсолютным приоритетом (PREEMPT)",
        "desc": "Система с двумя потоками заявок: обычные и срочные. Срочные заявки вытесняют обычные из прибора с сохранением оставшегося времени.",
        "code": """* МОДЕЛЬ: СМО с вытеснением приоритетными заявками (PREEMPT / RETURN)
* Описание: Срочные заявки прерывают обслуживание обычных

* Поток 1: Обычные клиенты (приоритет 1)
  GENERATE 12,5,,,1     ; Приоритет = 1
  QUEUE USUAL_Q
  SEIZE DOCTOR
  DEPART USUAL_Q
  ADVANCE 10,4
  RELEASE DOCTOR
  TERMINATE 1

* Поток 2: Экстренные вызовы (приоритет 2)
  GENERATE 60,30,,,2    ; Приоритет = 2
  QUEUE URGENT_Q
  PREEMPT DOCTOR,PR     ; Вытеснение обычного пациента с сохранением остатка
  DEPART URGENT_Q
  ADVANCE 15,5          ; Неотложная помощь
  RETURN DOCTOR         ; Возврат прибора вытесненному пациенту
  TERMINATE 1

  START 200
  END
"""
    },
    {
        "title": "4. СМО с отказами (ограниченная очередь / TEST)",
        "desc": "Система с конечной емкостью буфера ожидания. Если в очереди уже 3 заявки, транзакт покидает систему (отказ в обслуживании).",
        "code": """* МОДЕЛЬ: СМО с ограниченной очередью (не более 3 мест)
* Описание: Проверка длины очереди через блок TEST

  GENERATE 8,3               ; Поток заявок
  TEST LE Q$BUFFER,3,REJECT  ; Проверка: длина очереди <= 3? Если ложно -> REJECT
  QUEUE BUFFER               ; Вход в буфер
  SEIZE OPERATOR
  DEPART BUFFER
  ADVANCE 9,4                ; Обслуживание
  RELEASE OPERATOR
  TERMINATE 1                ; Успешно обслужен

REJECT TERMINATE 0           ; Уход без обслуживания (отказ)

  START 500
  END
"""
    },
    {
        "title": "5. Двухфазная линия обслуживания (Конвейер)",
        "desc": "Последовательное обслуживание деталей на двух станках (токарный и фрезерный) с промежуточным буфером.",
        "code": """* МОДЕЛЬ: Двухфазный производственный участок
* Описание: Станок 1 (LATHE) -> Буфер -> Станок 2 (MILLING)

  GENERATE 20,8         ; Поступление заготовок
  QUEUE Q_STATION1
  SEIZE LATHE           ; Фаза 1: Токарная обработка
  DEPART Q_STATION1
  ADVANCE 14,4
  RELEASE LATHE

  QUEUE Q_STATION2
  SEIZE MILLING         ; Фаза 2: Фрезерная обработка
  DEPART Q_STATION2
  ADVANCE 16,5
  RELEASE MILLING

  TERMINATE 1           ; Готовая деталь

  START 300
  END
"""
    }
]


class TemplatesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор шаблона модели GPSS")
        self.resize(750, 500)
        self.selected_code = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl_header = QLabel("Выберите готовый шаблон для быстрого старта:")
        lbl_header.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl_header)

        splitter = QSplitter(Qt.Horizontal)

        # Список шаблонов
        self.list_widget = QListWidget()
        for t in TEMPLATES:
            self.list_widget.addItem(t["title"])
        self.list_widget.currentRowChanged.connect(self._on_template_selected)
        splitter.addWidget(self.list_widget)

        # Правая панель: описание и предпросмотр кода
        right_panel = QVBoxLayout()
        right_container = QSplitter(Qt.Vertical)

        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setObjectName("template_desc")
        self.lbl_desc.setStyleSheet("padding: 4px;")
        right_container.addWidget(self.lbl_desc)

        self.code_preview = QTextEdit()
        self.code_preview.setObjectName("code_preview")
        self.code_preview.setReadOnly(True)
        self.code_preview.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        right_container.addWidget(self.code_preview)
        right_container.setStretchFactor(0, 1)
        right_container.setStretchFactor(1, 4)

        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_apply = QPushButton("Вставить в редактор")
        btn_apply.setObjectName("btn_save")
        btn_apply.clicked.connect(self._apply)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_apply)
        layout.addLayout(btn_layout)

        if TEMPLATES:
            self.list_widget.setCurrentRow(0)

    def _on_template_selected(self, index):
        if 0 <= index < len(TEMPLATES):
            t = TEMPLATES[index]
            self.lbl_desc.setText(t["desc"])
            self.code_preview.setPlainText(t["code"])

    def _apply(self):
        idx = self.list_widget.currentRow()
        if 0 <= idx < len(TEMPLATES):
            self.selected_code = TEMPLATES[idx]["code"]
            self.accept()

