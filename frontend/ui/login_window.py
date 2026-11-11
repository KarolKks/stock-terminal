from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
)

from ui.login_form import LoginForm
from ui.register_form import RegisterForm
from ui.chart_widget import StockChartWidget
from ui.styles import WHITE, NAVY
from api.client import ApiClient


class LoginWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Terminal – Logowanie")
        self.setMinimumSize(1000, 650)
        self.resize(1100, 700)

        self.api = ApiClient()

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background-color: {WHITE}; border-radius: 12px;")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.form_stack = QStackedWidget()
        self.form_stack.setStyleSheet(f"background-color: {WHITE};")

        self.login_form = LoginForm()
        self.register_form = RegisterForm()

        self.form_stack.addWidget(self.login_form)   
        self.form_stack.addWidget(self.register_form) 

        main_layout.addWidget(self.form_stack, stretch=2)

        chart_container = QWidget()
        chart_container.setStyleSheet(f"background-color: {NAVY}; border-radius: 0 12px 12px 0;")
        chart_layout = QHBoxLayout(chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)

        self.chart = StockChartWidget()
        chart_layout.addWidget(self.chart)

        main_layout.addWidget(chart_container, stretch=3)

    def _connect_signals(self):
        self.login_form.login_requested.connect(self._handle_login)
        self.login_form.switch_to_register.connect(self._show_register)

        self.register_form.register_requested.connect(self._handle_register)
        self.register_form.switch_to_login.connect(self._show_login)

    def _show_register(self):
        self.login_form.clear_fields()
        self.form_stack.setCurrentIndex(1)

    def _show_login(self):
        self.register_form.clear_fields()
        self.form_stack.setCurrentIndex(0)

    def _handle_login(self, username: str, password: str):
        try:
            self.api.login(username, password)
            self.login_form.show_success("Zalogowano pomyślnie!")
            QMessageBox.information(
                self,
                "Sukces",
                f"Zalogowano jako {username}.\n\nAccess token otrzymany.",
            )
        except Exception as exc:
            detail = self._extract_detail(exc)
            self.login_form.show_error(detail)

    def _handle_register(self, username: str, email: str, first_name: str, last_name: str, password: str):
        try:
            self.api.register(
                username=username,
                email=email,
                first_name=first_name,
                password=password,
                last_name=last_name,
            )
            self.register_form.clear_fields()
            self.form_stack.setCurrentIndex(0)
            self.login_form.show_success("Konto utworzone! Możesz się teraz zalogować.")
        except Exception as exc:
            detail = self._extract_detail(exc)
            self.register_form.show_error(detail)
            
    @staticmethod
    def _extract_detail(exc: Exception) -> str:
        try:
            import json
            resp = getattr(exc, "response", None)
            if resp is not None:
                data = resp.json()
                return data.get("detail", str(exc))
        except Exception:
            pass

        msg = str(exc)
        if "ConnectionError" in msg or "Connection refused" in msg:
            return "Nie można połączyć się z serwerem. Sprawdź, czy backend działa."
        return msg
