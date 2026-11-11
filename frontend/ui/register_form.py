from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
)
from PySide6.QtGui import QCursor

from ui.styles import (
    INPUT_STYLE,
    BUTTON_PRIMARY_STYLE,
    LABEL_STYLE,
    LINK_STYLE,
    STATUS_ERROR_STYLE,
    STATUS_SUCCESS_STYLE,
    TITLE_STYLE,
    SUBTITLE_STYLE,
)


class RegisterForm(QWidget):
    register_requested = Signal(str, str, str, str, str)
    switch_to_login = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(32, 24, 32, 24)
        outer.addStretch(1)

        container = QWidget()
        container.setFixedWidth(360)

        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        root.addStretch(1)

        lbl_app = QLabel("Stock Terminal")
        lbl_app.setStyleSheet("QLabel { font-size: 18px; font-weight: 700; color: #2B2D6E; }")
        root.addWidget(lbl_app)

        root.addSpacerItem(QSpacerItem(0, 10))

        lbl_title = QLabel("Rejestracja")
        lbl_title.setStyleSheet(TITLE_STYLE)
        root.addWidget(lbl_title)

        row_sub = QHBoxLayout()
        row_sub.setSpacing(4)
        lbl_sub = QLabel("Masz już konto?")
        lbl_sub.setStyleSheet(SUBTITLE_STYLE)
        row_sub.addWidget(lbl_sub)

        lbl_login = QLabel("<a href='#' style='color:#3F51B5; text-decoration:none;'>Zaloguj się</a>")
        lbl_login.setStyleSheet(LINK_STYLE)
        lbl_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lbl_login.linkActivated.connect(lambda: self.switch_to_login.emit())
        row_sub.addWidget(lbl_login)
        row_sub.addStretch()
        root.addLayout(row_sub)

        root.addSpacerItem(QSpacerItem(0, 10))

        self._add_field(root, "Nazwa użytkownika")
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Wpisz nazwę użytkownika")
        self.input_username.setStyleSheet(INPUT_STYLE)
        root.addWidget(self.input_username)
        root.addSpacerItem(QSpacerItem(0, 4))

        self._add_field(root, "Email")
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Wpisz adres e-mail")
        self.input_email.setStyleSheet(INPUT_STYLE)
        root.addWidget(self.input_email)
        root.addSpacerItem(QSpacerItem(0, 4))

        self._add_field(root, "Imię")
        self.input_first_name = QLineEdit()
        self.input_first_name.setPlaceholderText("Wpisz imię")
        self.input_first_name.setStyleSheet(INPUT_STYLE)
        root.addWidget(self.input_first_name)
        root.addSpacerItem(QSpacerItem(0, 4))

        self._add_field(root, "Nazwisko (opcjonalnie)")
        self.input_last_name = QLineEdit()
        self.input_last_name.setPlaceholderText("Wpisz nazwisko")
        self.input_last_name.setStyleSheet(INPUT_STYLE)
        root.addWidget(self.input_last_name)
        root.addSpacerItem(QSpacerItem(0, 4))

        self._add_field(root, "Hasło")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Wpisz hasło (min. 6 znaków)")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet(INPUT_STYLE)
        root.addWidget(self.input_password)
        root.addSpacerItem(QSpacerItem(0, 4))

        self._add_field(root, "Potwierdź hasło")
        self.input_password2 = QLineEdit()
        self.input_password2.setPlaceholderText("Powtórz hasło")
        self.input_password2.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password2.setStyleSheet(INPUT_STYLE)
        self.input_password2.returnPressed.connect(self._on_register)
        root.addWidget(self.input_password2)

        root.addSpacerItem(QSpacerItem(0, 10))

        self.btn_register = QPushButton("Zarejestruj się")
        self.btn_register.setStyleSheet(BUTTON_PRIMARY_STYLE)
        self.btn_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_register.clicked.connect(self._on_register)
        root.addWidget(self.btn_register)

        root.addSpacerItem(QSpacerItem(0, 6))

        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(STATUS_ERROR_STYLE)
        root.addWidget(self.lbl_status)

        root.addStretch(1)

        outer.addWidget(container)
        outer.addStretch(1)

    @staticmethod
    def _add_field(layout: QVBoxLayout, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(LABEL_STYLE)
        layout.addWidget(lbl)

    def _on_register(self):
        username = self.input_username.text().strip()
        email = self.input_email.text().strip()
        first_name = self.input_first_name.text().strip()
        last_name = self.input_last_name.text().strip()
        password = self.input_password.text()
        password2 = self.input_password2.text()

        if not username or not email or not first_name or not password:
            self.show_error("Wypełnij wszystkie wymagane pola.")
            return
        if len(password) < 6:
            self.show_error("Hasło musi mieć co najmniej 6 znaków.")
            return
        if password != password2:
            self.show_error("Hasła nie są identyczne.")
            return

        self.lbl_status.setText("")
        self.register_requested.emit(username, email, first_name, last_name, password)

    def show_error(self, msg: str):
        self.lbl_status.setStyleSheet(STATUS_ERROR_STYLE)
        self.lbl_status.setText(msg)

    def show_success(self, msg: str):
        self.lbl_status.setStyleSheet(STATUS_SUCCESS_STYLE)
        self.lbl_status.setText(msg)

    def clear_fields(self):
        self.input_username.clear()
        self.input_email.clear()
        self.input_first_name.clear()
        self.input_last_name.clear()
        self.input_password.clear()
        self.input_password2.clear()
        self.lbl_status.clear()
