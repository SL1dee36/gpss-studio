from PySide6.QtGui import QColor

GPSS_KEYWORDS = [
    "GENERATE", "TERMINATE", "SEIZE", "RELEASE", "ADVANCE",
    "QUEUE", "DEPART", "ENTER", "LEAVE", "STORAGE", "TRANSFER",
    "TEST", "ASSIGN", "MARK", "PRIORITY", "SPLIT", "ASSEMBLE",
    "GATHER", "MATCH", "PREEMPT", "RETURN", "SAVEVALUE",
    "MSAVEVALUE", "TABULATE", "GATE", "SELECT", "COUNT",
    "INDEX", "PRINT", "LOGIC", "BUFFER", "LINK", "UNLINK"
]

GPSS_DIRECTIVES = [
    "START", "END", "CLEAR", "RESET", "FUNCTION", "VARIABLE",
    "BVARIABLE", "FVARIABLE", "INITIAL", "TABLE", "QTABLE",
    "SIMULATE", "DO", "ENDDO", "IF", "ELSE", "ENDIF", "GOTO",
    "INCLUDE", "INTEGER", "REAL", "AMPER", "PUTPIC", "PUTSTRING",
    "GETLIST"
]

GPSS_CORE_KEYWORDS = set(GPSS_KEYWORDS + GPSS_DIRECTIVES)

DEFAULT_TEMPLATE = """"""
CODE_VAR_16 = DEFAULT_TEMPLATE
GITHUB_URL = "https://github.com/SL1dee36/gpss-studio"
BLOCK_COLORS_DARK = {
    'GENERATE': QColor('#238636'),
    'TERMINATE': QColor('#da3633'),
    'QUEUE': QColor('#1f6feb'),
    'DEPART': QColor('#388bfd'),
    'SEIZE': QColor('#8957e5'),
    'RELEASE': QColor('#a371f7'),
    'PREEMPT': QColor('#8957e5'),
    'RETURN': QColor('#a371f7'),
    'ENTER': QColor('#8957e5'),
    'LEAVE': QColor('#a371f7'),
    'ADVANCE': QColor('#d29922'),
    'TRANSFER': QColor('#db61a2'),
    'TEST': QColor('#f0883e'),
    'GATE': QColor('#f0883e'),
    'LOOP': QColor('#f0883e'),
    'SPLIT': QColor('#db61a2'),
    'ASSIGN': QColor('#6e7681'),
    'MARK': QColor('#6e7681'),
    'PRIORITY': QColor('#6e7681'),
    'OTHER': QColor('#6e7681')
}
BLOCK_COLORS_LIGHT = {
    'GENERATE': QColor('#1a7f37'),
    'TERMINATE': QColor('#cf222e'),
    'QUEUE': QColor('#0969da'),
    'DEPART': QColor('#218bff'),
    'SEIZE': QColor('#8250df'),
    'RELEASE': QColor('#a475f9'),
    'PREEMPT': QColor('#8250df'),
    'RETURN': QColor('#a475f9'),
    'ENTER': QColor('#8250df'),
    'LEAVE': QColor('#a475f9'),
    'ADVANCE': QColor('#b78103'),
    'TRANSFER': QColor('#bf3989'),
    'TEST': QColor('#d47616'),
    'GATE': QColor('#d47616'),
    'LOOP': QColor('#d47616'),
    'SPLIT': QColor('#bf3989'),
    'ASSIGN': QColor('#57606a'),
    'MARK': QColor('#57606a'),
    'PRIORITY': QColor('#57606a'),
    'OTHER': QColor('#57606a')
}
GPSS_FLOWCHART_BLOCKS = {
    "GENERATE", "TERMINATE", "SEIZE", "RELEASE", "ADVANCE",
    "QUEUE", "DEPART", "ENTER", "LEAVE", "TRANSFER",
    "TEST", "ASSIGN", "MARK", "PRIORITY", "SPLIT", "ASSEMBLE",
    "GATHER", "MATCH", "PREEMPT", "RETURN", "SAVEVALUE",
    "MSAVEVALUE", "TABULATE", "GATE", "SELECT", "COUNT",
    "INDEX", "PRINT", "LOGIC", "BUFFER", "LINK", "UNLINK", "LOOP"
}
