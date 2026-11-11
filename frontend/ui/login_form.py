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


class LoginForm(QWidget):
    login_requested = Signal(str, str)
    switch_to_register = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.addStretch(1)

        container = QWidget()
        container.setFixedWidth(360)

        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        root.addStretch(1)

        lbl_app = QLabel("Stock Terminal")
        lbl_app.setStyleSheet("QLabel { font-size: 18px; font-weight: 700; color: #2B2D6E; }")
        root.addWidget(lbl_app)

        root.addSpacerItem(QSpacerItem(0, 16))

        lbl_title = QLabel("Zaloguj się")
        lbl_title.setStyleSheet(TITLE_STYLE)
        root.addWidget(lbl_title)

        row_sub = QHBoxLayout()
        row_sub.setSpacing(4)
        lbl_sub = QLabel("Nie masz konta?")
        lbl_sub.setStyleSheet(SUBTITLE_STYLE)
        row_sub.addWidget(lbl_sub)

        lbl_register = QLabel("<a href='#' style='color:#3F51B5; text-decoration:none;'>Utwórz konto</a>")
        lbl_register.setStyleSheet(LINK_STYLE)
        lbl_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lbl_register.linkActivated.connect(lambda: self.switch_to_register.emit())
        row_sub.addWidget(lbl_register)
        row_sub.addStretch()
        root.addLayout(row_sub)

        root.addSpacerItem(QSpacerItem(0, 16))

        lbl_user = QLabel("Nazwa użytkownika")
        lbl_user.setStyleSheet(LABEL_STYLE)
        root.addWidget(lbl_user)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Wpisz nazwę użytkownika")
        self.input_username.setStyleSheet(INPUT_STYLE)
        root.addWidget(self.input_username)

        root.addSpacerItem(QSpacerItem(0, 8))

        lbl_pass = QLabel("Hasło")
        lbl_pass.setStyleSheet(LABEL_STYLE)
        root.addWidget(lbl_pass)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Wpisz hasło")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet(INPUT_STYLE)
        self.input_password.returnPressed.connect(self._on_login)
        root.addWidget(self.input_password)

        row_pass_opts = QHBoxLayout()
        row_pass_opts.addStretch()
        self.btn_toggle_pass = QPushButton("👁 Pokaż")
        self.btn_toggle_pass.setFlat(True)
        self.btn_toggle_pass.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_toggle_pass.setStyleSheet("QPushButton { color: #757575; font-size: 12px; border: none; }")
        self.btn_toggle_pass.clicked.connect(self._toggle_password)
        row_pass_opts.addWidget(self.btn_toggle_pass)
        root.addLayout(row_pass_opts)

        root.addSpacerItem(QSpacerItem(0, 10))

        self.btn_login = QPushButton("Zaloguj się")
        self.btn_login.setStyleSheet(BUTTON_PRIMARY_STYLE)
        self.btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_login.clicked.connect(self._on_login)
        root.addWidget(self.btn_login)

        root.addSpacerItem(QSpacerItem(0, 10))

        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(STATUS_ERROR_STYLE)
        root.addWidget(self.lbl_status)

        root.addStretch(1)

        outer.addWidget(container)
        outer.addStretch(1)

    def _on_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()
        if not username or not password:
            self.show_error("Wypełnij wszystkie pola.")
            return
        self.lbl_status.setText("")
        self.login_requested.emit(username, password)

    def _toggle_password(self):
        if self.input_password.echoMode() == QLineEdit.EchoMode.Password:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_pass.setText("🔒 Ukryj")
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_pass.setText("👁 Pokaż")

    def show_error(self, msg: str):
        self.lbl_status.setStyleSheet(STATUS_ERROR_STYLE)
        self.lbl_status.setText(msg)

    def show_success(self, msg: str):
        self.lbl_status.setStyleSheet(STATUS_SUCCESS_STYLE)
        self.lbl_status.setText(msg)

    def clear_fields(self):
        self.input_username.clear()
        self.input_password.clear()
        self.lbl_status.clear()
