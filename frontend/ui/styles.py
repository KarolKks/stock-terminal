NAVY = "#2B2D6E"
NAVY_DARK = "#1E2057"
PRIMARY_BLUE = "#3F51B5"
PRIMARY_BLUE_HOVER = "#354499"
WHITE = "#FFFFFF"
LIGHT_GREY_BG = "#F8F9FC"
BORDER_GREY = "#D0D0D0"
TEXT_DARK = "#212121"
TEXT_MUTED = "#757575"
LINK_BLUE = "#3F51B5"
ERROR_RED = "#D32F2F"
SUCCESS_GREEN = "#388E3C"

INPUT_STYLE = f"""
    QLineEdit {{
        border: 1px solid {BORDER_GREY};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        background: {WHITE};
        color: {TEXT_DARK};
    }}
    QLineEdit:focus {{
        border: 2px solid {PRIMARY_BLUE};
    }}
"""

BUTTON_PRIMARY_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_BLUE};
        color: {WHITE};
        border: none;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_BLUE_HOVER};
    }}
    QPushButton:pressed {{
        background-color: #2C3A8C;
    }}
    QPushButton:disabled {{
        background-color: #9FA8DA;
    }}
"""

BUTTON_SECONDARY_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {PRIMARY_BLUE};
        border: 1px solid {PRIMARY_BLUE};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #E8EAF6;
    }}
"""

BUTTON_DANGER_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {ERROR_RED};
        border: 1px solid {ERROR_RED};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #FFEBEE;
    }}
"""

BUTTON_SMALL_STYLE = f"""
    QPushButton {{
        background-color: #E8EAF6;
        color: {PRIMARY_BLUE};
        border: 1px solid #C5CAE9;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #D3D8F2;
    }}
"""

COMBOBOX_STYLE = f"""
    QComboBox {{
        border: 1px solid {BORDER_GREY};
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 13px;
        background: {WHITE};
        color: {TEXT_DARK};
        min-height: 22px;
    }}
    QComboBox:focus {{
        border: 2px solid {PRIMARY_BLUE};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid {BORDER_GREY};
        selection-background-color: {PRIMARY_BLUE};
        selection-color: {WHITE};
        background-color: {WHITE};
        color: {TEXT_DARK};
        padding: 4px;
        outline: none;
    }}
"""

LIST_STYLE = f"""
    QListWidget {{
        border: 1px solid {BORDER_GREY};
        border-radius: 6px;
        background: {WHITE};
        color: {TEXT_DARK};
        padding: 4px;
        outline: none;
        font-size: 13px;
    }}
    QListWidget::item {{
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 2px;
    }}
    QListWidget::item:hover {{
        background-color: #E8EAF6;
    }}
    QListWidget::item:selected {{
        background-color: {PRIMARY_BLUE};
        color: {WHITE};
        font-weight: 600;
    }}
"""

LABEL_STYLE = f"""
    QLabel {{
        color: {TEXT_DARK};
        font-size: 13px;
    }}
"""

LINK_STYLE = f"""
    QLabel {{
        color: {LINK_BLUE};
        font-size: 13px;
    }}
    QLabel:hover {{
        text-decoration: underline;
    }}
"""

STATUS_ERROR_STYLE = f"""
    QLabel {{
        color: {ERROR_RED};
        font-size: 12px;
    }}
"""

STATUS_SUCCESS_STYLE = f"""
    QLabel {{
        color: {SUCCESS_GREEN};
        font-size: 12px;
    }}
"""

TITLE_STYLE = f"""
    QLabel {{
        color: {TEXT_DARK};
        font-size: 26px;
        font-weight: 700;
    }}
"""

SUBTITLE_STYLE = f"""
    QLabel {{
        color: {TEXT_MUTED};
        font-size: 13px;
    }}
"""
