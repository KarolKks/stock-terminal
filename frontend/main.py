"""
Stock Terminal – PySide6 desktop application entry point.
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase

from ui.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)

    # ── Load custom Inter font ─────────────────────────────────────────
    font_path = Path(__file__).parent / "assets" / "fonts" / "Inter-Variable.ttf"
    if font_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            app.setFont(QFont("Inter", 10))
        else:
            app.setFont(QFont("Segoe UI", 10))
    else:
        app.setFont(QFont("Segoe UI", 10))

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
