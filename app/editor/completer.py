import re
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtWidgets import QCompleter

from app.consts import GPSS_CORE_KEYWORDS

# Документация и подсказки по параметрам блоков GPSS/H
GPSS_BLOCK_DOCS = {
    "GENERATE": "GENERATE A,B,C,D,E\n  A: Среднее время между транзактами\n  B: Полуразмах или модификатор\n  C: Время первого транзакта\n  D: Общий лимит транзактов\n  E: Приоритет",
    "TERMINATE": "TERMINATE [A]\n  A: Уменьшение счётчика завершений (START)",
    "ADVANCE": "ADVANCE A,B\n  A: Среднее время обслуживания\n  B: Полуразмах или модификатор",
    "SEIZE": "SEIZE A\n  A: Имя или номер прибора (Facility) для занятия",
    "RELEASE": "RELEASE A\n  A: Имя или номер прибора (Facility) для освобождения",
    "PREEMPT": "PREEMPT A,[B],[C],[D],[E]\n  A: Имя прибора для вытеснения с приоритетом\n  B: Режим приоритета (PR)",
    "RETURN": "RETURN A\n  A: Имя прибора после вытеснения",
    "QUEUE": "QUEUE A,[B]\n  A: Имя очереди\n  B: Число добавляемых единиц (по умолч. 1)",
    "DEPART": "DEPART A,[B]\n  A: Имя очереди\n  B: Число вычитаемых единиц (по умолч. 1)",
    "ENTER": "ENTER A,[B]\n  A: Имя памяти (Storage)\n  B: Занимаемая ёмкость (по умолч. 1)",
    "LEAVE": "LEAVE A,[B]\n  A: Имя памяти (Storage)\n  B: Освобождаемая ёмкость (по умолч. 1)",
    "STORAGE": "STORAGE S(A)\n  A: Ёмкость многоканального накопителя",
    "TRANSFER": "TRANSFER [A],B,[C]\n  A: Режим (дробь .XX, BOTH, ALL, PICK)\n  B: Адрес перехода 1\n  C: Адрес перехода 2",
    "TEST": "TEST X A,B,[C]\n  X: Оператор (L, LE, E, NE, G, GE)\n  A, B: Операнды сравнения (SNA или константы)\n  C: Метка перехода, если условие ложно",
    "ASSIGN": "ASSIGN A,B,[C]\n  A: Номер или имя параметра транзакта\n  B: Присваиваемое значение\n  C: Номер функции",
    "SAVEVALUE": "SAVEVALUE A,B,[C]\n  A: Имя или номер ячейки сохранения\n  B: Записываемое значение",
    "TABULATE": "TABULATE A,[B]\n  A: Имя таблицы частот (TABLE)\n  B: Вес выборки (по умолч. 1)",
    "TABLE": "TABLE A,B,C,D\n  A: Исследуемый аргумент (M1, Q$LINE и т.д.)\n  B: Верхняя граница 1-го интервала\n  C: Ширина интервала\n  D: Число интервалов",
    "START": "START A,[B],[C],[D]\n  A: Число завершений для остановки симуляции\n  B: NP (подавление листинга)",
    "CLEAR": "CLEAR [A]\n  Сброс статистики модели без удаления транзактов",
    "RESET": "RESET [A]\n  Сброс статистики с сохранением транзактов",
    "SPLIT": "SPLIT A,B,[C]\n  A: Число создаваемых копий транзакта\n  B: Метка перехода для копий",
    "ASSEMBLE": "ASSEMBLE A\n  A: Число собираемых транзактов одного семейства",
    "GATE": "GATE X A,[B]\n  X: Условие (LS, LR, U, NU, SF, SNF, SE, SNE)\n  A: Имя ключа, прибора или накопителя\n  B: Адрес перехода при закрытых воротах",
    "LOOP": "LOOP A,B\n  A: Номер параметра цикла\n  B: Метка перехода, пока параметр > 0",
    "PRIORITY": "PRIORITY A,[B]\n  A: Значение приоритета транзакта",
    "MARK": "MARK [A]\n  A: Параметр для записи времени входа (время транзита M1)",
}

# Стандартные числовые атрибуты (SNA)
GPSS_SNA_VARIABLES = [
    "C1", "M1", "PR", "AC1",
    "RN1", "RN2", "RN3", "RN4", "RN5", "RN6", "RN7",
    "Q$", "QA$", "QC$", "QM$", "QT$", "QX$",
    "F$", "FR$", "FC$", "FT$",
    "S$", "SA$", "SC$", "SM$", "ST$", "SR$",
    "V$", "BV$", "X$", "TB$"
]


class GPSSCompleter(QCompleter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStringListModel(self)
        self.setModel(self.model)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setWrapAround(False)
        self.base_words = sorted(list(GPSS_CORE_KEYWORDS) + GPSS_SNA_VARIABLES)
        self.update_words("")

    def extract_model_entities(self, text):
        """Извлекает имена очередей, приборов, накопителей и меток из текста модели."""
        entities = set()

        # Приборы: SEIZE / RELEASE / PREEMPT / RETURN
        for m in re.finditer(r"\b(?:SEIZE|RELEASE|PREEMPT|RETURN)\s+([A-Za-z0-9_]+)", text, re.IGNORECASE):
            entities.add(m.group(1).upper())

        # Очереди: QUEUE / DEPART
        for m in re.finditer(r"\b(?:QUEUE|DEPART)\s+([A-Za-z0-9_]+)", text, re.IGNORECASE):
            entities.add(m.group(1).upper())

        # Накопители: ENTER / LEAVE / name STORAGE
        for m in re.finditer(r"\b(?:ENTER|LEAVE)\s+([A-Za-z0-9_]+)", text, re.IGNORECASE):
            entities.add(m.group(1).upper())
        for m in re.finditer(r"^([A-Za-z0-9_]+)\s+STORAGE\b", text, re.MULTILINE | re.IGNORECASE):
            entities.add(m.group(1).upper())

        # Таблицы: TABULATE / name TABLE
        for m in re.finditer(r"\bTABULATE\s+([A-Za-z0-9_]+)", text, re.IGNORECASE):
            entities.add(m.group(1).upper())
        for m in re.finditer(r"^([A-Za-z0-9_]+)\s+TABLE\b", text, re.MULTILINE | re.IGNORECASE):
            entities.add(m.group(1).upper())

        # Метки переходов (TRANSFER, TEST и метки в начале строки)
        for m in re.finditer(r"^([A-Za-z0-9_]+)\b(?!\s*(?:STORAGE|TABLE|VARIABLE|FUNCTION|INITIAL))", text, re.MULTILINE):
            w = m.group(1).upper()
            if w not in GPSS_CORE_KEYWORDS and not w.startswith("*"):
                entities.add(w)

        return entities

    def update_words(self, current_code=""):
        entities = self.extract_model_entities(current_code) if current_code else set()
        all_words = sorted(set(self.base_words) | entities)
        self.model.setStringList(all_words)

    def apply_style(self, theme="dark"):
        if theme == "dark":
            style = """
                QAbstractItemView {
                    background-color: #1a1f22;
                    color: #d8e2ec;
                    border: 1px solid #30363d;
                    selection-background-color: #1f6feb;
                    selection-color: #ffffff;
                    font-family: Consolas, monospace;
                    font-size: 12px;
                    padding: 2px;
                }
            """
        else:
            style = """
                QAbstractItemView {
                    background-color: #ffffff;
                    color: #24292f;
                    border: 1px solid #d0d7de;
                    selection-background-color: #0969da;
                    selection-color: #ffffff;
                    font-family: Consolas, monospace;
                    font-size: 12px;
                    padding: 2px;
                }
            """
        self.popup().setStyleSheet(style)

