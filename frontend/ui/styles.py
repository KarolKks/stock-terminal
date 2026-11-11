"""
Centralised colour palette and QSS stylesheets for the application.
"""

# ── Colour palette ────────────────────────────────────────────────────────
NAVY = "#2B2D6E"
PRIMARY_BLUE = "#3F51B5"
PRIMARY_BLUE_HOVER = "#354499"
WHITE = "#FFFFFF"
LIGHT_GREY_BG = "#F5F5F5"
BORDER_GREY = "#D0D0D0"
TEXT_DARK = "#212121"
TEXT_MUTED = "#757575"
LINK_BLUE = "#3F51B5"
ERROR_RED = "#D32F2F"
SUCCESS_GREEN = "#388E3C"

# ── Reusable stylesheet fragments ────────────────────────────────────────

INPUT_STYLE = f"""
    QLineEdit {{
        border: 1px solid {BORDER_GREY};
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 14px;
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
        padding: 12px;
        font-size: 14px;
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
        padding: 10px;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #E8EAF6;
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
