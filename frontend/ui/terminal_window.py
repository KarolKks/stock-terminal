from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
    QMessageBox,
    QFrame,
    QSplitter,
)

from api.client import ApiClient, ApiError
from ui.market_chart_widget import MarketChartWidget
from ui.styles import (
    NAVY,
    PRIMARY_BLUE,
    WHITE,
    LIGHT_GREY_BG,
    BORDER_GREY,
    TEXT_DARK,
    TEXT_MUTED,
    INPUT_STYLE,
    BUTTON_PRIMARY_STYLE,
    BUTTON_SECONDARY_STYLE,
    BUTTON_DANGER_STYLE,
    BUTTON_SMALL_STYLE,
    COMBOBOX_STYLE,
    LIST_STYLE,
    STATUS_ERROR_STYLE,
    STATUS_SUCCESS_STYLE,
)
from utils.worker import run_in_background


class TerminalWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, api: ApiClient, username: str = "", parent=None):
        super().__init__(parent)
        self.api = api
        self.username = username

        self.categories = []
        self.current_category = None
        self.current_ticker = ""

        self.setWindowTitle("Stock Terminal – Pulpit inwestora")
        self.setMinimumSize(1050, 700)
        self.resize(1200, 780)

        self._build_ui()
        self.load_watchlists()

    def _build_ui(self):
        root_widget = QWidget()
        root_widget.setStyleSheet(f"background-color: {LIGHT_GREY_BG};")
        self.setCentralWidget(root_widget)

        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(16, 12, 16, 16)
        root_layout.setSpacing(12)

        header = QFrame()
        header.setStyleSheet(
            f"background-color: {WHITE}; border-radius: 8px; border: 1px solid {BORDER_GREY};"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)

        lbl_logo = QLabel("Stock Terminal")
        lbl_logo.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {NAVY}; border: none;"
        )
        header_layout.addWidget(lbl_logo)

        header_layout.addStretch()

        self.lbl_user = QLabel(f"Zalogowano jako: <b>{self.username}</b>")
        self.lbl_user.setStyleSheet(f"color: {TEXT_DARK}; font-size: 13px; border: none;")
        header_layout.addWidget(self.lbl_user)

        header_layout.addSpacing(16)

        self.btn_logout = QPushButton("Wyloguj")
        self.btn_logout.setStyleSheet(BUTTON_SECONDARY_STYLE)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.clicked.connect(self._on_logout_clicked)
        header_layout.addWidget(self.btn_logout)

        root_layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            "QSplitter::handle { background-color: #E0E0E0; width: 2px; }"
        )

        panel_watchlist = QFrame()
        panel_watchlist.setStyleSheet(
            f"background-color: {WHITE}; border-radius: 8px; border: 1px solid {BORDER_GREY};"
        )
        layout_wl = QVBoxLayout(panel_watchlist)
        layout_wl.setContentsMargins(16, 16, 16, 16)
        layout_wl.setSpacing(10)

        lbl_wl_title = QLabel("Twoje Watchlisty")
        lbl_wl_title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {NAVY}; border: none;"
        )
        layout_wl.addWidget(lbl_wl_title)

        lbl_cat = QLabel("Kategoria:")
        lbl_cat.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; border: none;")
        layout_wl.addWidget(lbl_cat)

        self.combo_categories = QComboBox()
        self.combo_categories.setStyleSheet(COMBOBOX_STYLE)
        self.combo_categories.currentIndexChanged.connect(self._on_category_changed)
        layout_wl.addWidget(self.combo_categories)

        row_cat_actions = QHBoxLayout()
        row_cat_actions.setSpacing(6)

        self.btn_add_cat = QPushButton("+ Nowa")
        self.btn_add_cat.setStyleSheet(BUTTON_SMALL_STYLE)
        self.btn_add_cat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_cat.clicked.connect(self._on_create_category)
        row_cat_actions.addWidget(self.btn_add_cat)

        self.btn_edit_cat = QPushButton("Zmień nazwę")
        self.btn_edit_cat.setStyleSheet(BUTTON_SMALL_STYLE)
        self.btn_edit_cat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_cat.clicked.connect(self._on_rename_category)
        row_cat_actions.addWidget(self.btn_edit_cat)

        self.btn_del_cat = QPushButton("Usuń")
        self.btn_del_cat.setStyleSheet(BUTTON_DANGER_STYLE)
        self.btn_del_cat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del_cat.clicked.connect(self._on_delete_category)
        row_cat_actions.addWidget(self.btn_del_cat)

        layout_wl.addLayout(row_cat_actions)

        lbl_tickers = QLabel("Akcje w kategorii:")
        lbl_tickers.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; border: none; margin-top: 6px;")
        layout_wl.addWidget(lbl_tickers)

        self.list_tickers = QListWidget()
        self.list_tickers.setStyleSheet(LIST_STYLE)
        self.list_tickers.itemClicked.connect(self._on_ticker_item_clicked)
        layout_wl.addWidget(self.list_tickers)

        lbl_add_t = QLabel("Dodaj ticker do kategorii:")
        lbl_add_t.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; border: none;")
        layout_wl.addWidget(lbl_add_t)

        row_add_ticker = QHBoxLayout()
        row_add_ticker.setSpacing(6)

        self.input_ticker = QLineEdit()
        self.input_ticker.setPlaceholderText("np. AAPL, TSLA")
        self.input_ticker.setStyleSheet(INPUT_STYLE)
        self.input_ticker.returnPressed.connect(self._on_add_ticker)
        row_add_ticker.addWidget(self.input_ticker)

        self.btn_add_ticker = QPushButton("+ Dodaj")
        self.btn_add_ticker.setStyleSheet(BUTTON_PRIMARY_STYLE)
        self.btn_add_ticker.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_ticker.clicked.connect(self._on_add_ticker)
        row_add_ticker.addWidget(self.btn_add_ticker)

        layout_wl.addLayout(row_add_ticker)

        self.btn_remove_ticker = QPushButton("Usuń zaznaczony ticker")
        self.btn_remove_ticker.setStyleSheet(BUTTON_DANGER_STYLE)
        self.btn_remove_ticker.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove_ticker.clicked.connect(self._on_remove_ticker)
        layout_wl.addWidget(self.btn_remove_ticker)

        self.lbl_wl_status = QLabel("")
        self.lbl_wl_status.setWordWrap(True)
        self.lbl_wl_status.setStyleSheet("border: none;")
        layout_wl.addWidget(self.lbl_wl_status)

        splitter.addWidget(panel_watchlist)

        panel_chart = QFrame()
        panel_chart.setStyleSheet(
            f"background-color: {NAVY}; border-radius: 8px; border: 1px solid {BORDER_GREY};"
        )
        layout_chart_panel = QVBoxLayout(panel_chart)
        layout_chart_panel.setContentsMargins(16, 12, 16, 12)
        layout_chart_panel.setSpacing(10)

        controls_bar = QFrame()
        controls_bar.setStyleSheet("background: transparent; border: none;")
        controls_layout = QHBoxLayout(controls_bar)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)

        lbl_select_ticker = QLabel("Akcja:")
        lbl_select_ticker.setStyleSheet("color: white; font-weight: 600; font-size: 13px;")
        controls_layout.addWidget(lbl_select_ticker)

        self.combo_ticker = QComboBox()
        self.combo_ticker.setEditable(True)
        self.combo_ticker.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_ticker.setStyleSheet(COMBOBOX_STYLE)
        self.combo_ticker.setMinimumWidth(120)
        self.combo_ticker.currentTextChanged.connect(self._on_ticker_selection_changed)
        controls_layout.addWidget(self.combo_ticker)

        lbl_period = QLabel("Okres:")
        lbl_period.setStyleSheet("color: white; font-size: 13px;")
        controls_layout.addWidget(lbl_period)

        self.combo_period = QComboBox()
        self.combo_period.setStyleSheet(COMBOBOX_STYLE)
        self.combo_period.addItems(["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"])
        self.combo_period.setCurrentText("6mo")
        self.combo_period.currentTextChanged.connect(self._on_chart_params_changed)
        controls_layout.addWidget(self.combo_period)

        lbl_interval = QLabel("Interwał:")
        lbl_interval.setStyleSheet("color: white; font-size: 13px;")
        controls_layout.addWidget(lbl_interval)

        self.combo_interval = QComboBox()
        self.combo_interval.setStyleSheet(COMBOBOX_STYLE)
        self.combo_interval.addItems(["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"])
        self.combo_interval.setCurrentText("1d")
        self.combo_interval.currentTextChanged.connect(self._on_chart_params_changed)
        controls_layout.addWidget(self.combo_interval)

        self.btn_refresh_chart = QPushButton("Odśwież")
        self.btn_refresh_chart.setStyleSheet(BUTTON_SECONDARY_STYLE)
        self.btn_refresh_chart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh_chart.clicked.connect(self.load_candles)
        controls_layout.addWidget(self.btn_refresh_chart)

        self.btn_quick_add = QPushButton("+ Dodaj do watchlisty")
        self.btn_quick_add.setStyleSheet(BUTTON_SMALL_STYLE)
        self.btn_quick_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quick_add.clicked.connect(self._on_quick_add_to_watchlist)
        controls_layout.addWidget(self.btn_quick_add)

        controls_layout.addStretch()

        layout_chart_panel.addWidget(controls_bar)

        self.chart = MarketChartWidget()
        layout_chart_panel.addWidget(self.chart, stretch=1)

        self.lbl_chart_status = QLabel("")
        self.lbl_chart_status.setStyleSheet("color: #C5CAE9; font-size: 12px; border: none;")
        layout_chart_panel.addWidget(self.lbl_chart_status)

        splitter.addWidget(panel_chart)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        root_layout.addWidget(splitter, stretch=1)

    def load_watchlists(self, select_category_id: int = None, select_ticker: str = None):
        def _fetch():
            return self.api.get_watchlists()

        def _on_success(categories):
            self.categories = categories or []
            self.combo_categories.blockSignals(True)
            self.combo_categories.clear()

            target_idx = 0
            for idx, cat in enumerate(self.categories):
                self.combo_categories.addItem(cat["name"], cat["id"])
                if select_category_id and cat["id"] == select_category_id:
                    target_idx = idx

            self.combo_categories.blockSignals(False)

            if self.categories:
                self.combo_categories.setCurrentIndex(target_idx)
                self._update_selected_category_ui(select_ticker)
            else:
                self.current_category = None
                self.list_tickers.clear()
                self._update_ticker_combo([])
                self.chart.show_message("Utwórz pierwszą kategorię watchlisty po lewej stronie.")

        def _on_error(err_msg):
            self._show_wl_status(f"Błąd ładowania watchlisty: {err_msg}", is_error=True)

        run_in_background(_fetch, on_success=_on_success, on_error=_on_error)

    def _on_category_changed(self, index: int):
        if index < 0 or index >= len(self.categories):
            return
        self._update_selected_category_ui()

    def _update_selected_category_ui(self, select_ticker: str = None):
        cat_idx = self.combo_categories.currentIndex()
        if cat_idx < 0 or cat_idx >= len(self.categories):
            return

        self.current_category = self.categories[cat_idx]
        items = self.current_category.get("items", [])

        self.list_tickers.clear()
        ticker_names = []
        for item in items:
            t = item["ticker"]
            ticker_names.append(t)
            list_item = QListWidgetItem(f"  {t}")
            list_item.setData(Qt.ItemDataRole.UserRole, t)
            self.list_tickers.addItem(list_item)

        self._update_ticker_combo(ticker_names, select_ticker)

    def _update_ticker_combo(self, tickers: list[str], select_ticker: str = None):
        self.combo_ticker.blockSignals(True)
        current_text = select_ticker or self.combo_ticker.currentText().strip().upper()
        self.combo_ticker.clear()

        for t in tickers:
            self.combo_ticker.addItem(t)

        if select_ticker and select_ticker in tickers:
            self.combo_ticker.setCurrentText(select_ticker)
            chosen = select_ticker
        elif current_text and current_text in tickers:
            self.combo_ticker.setCurrentText(current_text)
            chosen = current_text
        elif tickers:
            self.combo_ticker.setCurrentIndex(0)
            chosen = tickers[0]
        else:
            if current_text:
                self.combo_ticker.setCurrentText(current_text)
                chosen = current_text
            else:
                chosen = ""

        self.combo_ticker.blockSignals(False)

        if chosen:
            self.current_ticker = chosen
            self.load_candles()

    def _on_create_category(self):
        name, ok = QInputDialog.getText(
            self,
            "Nowa kategoria",
            "Wprowadź nazwę nowej kategorii watchlisty (1-50 znaków):",
        )
        if not ok or not name.strip():
            return

        name = name.strip()

        def _create():
            return self.api.create_category(name)

        def _on_success(new_cat):
            self._show_wl_status(f"Utworzono kategorię '{new_cat['name']}'.", is_error=False)
            self.load_watchlists(select_category_id=new_cat["id"])

        def _on_error(err_msg):
            self._show_wl_status(f"Nie udało się utworzyć kategorii: {err_msg}", is_error=True)

        run_in_background(_create, on_success=_on_success, on_error=_on_error)

    def _on_rename_category(self):
        if not self.current_category:
            self._show_wl_status("Brak wybranej kategorii do edycji.", is_error=True)
            return

        cat_id = self.current_category["id"]
        current_name = self.current_category["name"]

        new_name, ok = QInputDialog.getText(
            self,
            "Zmień nazwę kategorii",
            f"Nowa nazwa dla '{current_name}':",
            text=current_name,
        )
        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()
        if new_name == current_name:
            return

        def _rename():
            return self.api.rename_category(cat_id, new_name)

        def _on_success(updated_cat):
            self._show_wl_status(f"Zmieniono nazwę na '{updated_cat['name']}'.", is_error=False)
            self.load_watchlists(select_category_id=updated_cat["id"])

        def _on_error(err_msg):
            self._show_wl_status(f"Błąd zmiany nazwy: {err_msg}", is_error=True)

        run_in_background(_rename, on_success=_on_success, on_error=_on_error)

    def _on_delete_category(self):
        if not self.current_category:
            return

        cat_id = self.current_category["id"]
        name = self.current_category["name"]

        reply = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć kategorię '{name}' wraz z jej zawartością?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _delete():
            return self.api.delete_category(cat_id)

        def _on_success(_):
            self._show_wl_status(f"Kategoria '{name}' została usunięta.", is_error=False)
            self.load_watchlists()

        def _on_error(err_msg):
            self._show_wl_status(f"Błąd usuwania kategorii: {err_msg}", is_error=True)

        run_in_background(_delete, on_success=_on_success, on_error=_on_error)

    def _on_add_ticker(self):
        ticker = self.input_ticker.text().strip().upper()
        if not ticker:
            self._show_wl_status("Wpisz symbol tickera.", is_error=True)
            return

        if not self.current_category:
            self._show_wl_status("Najpierw utwórz lub wybierz kategorię.", is_error=True)
            return

        cat_id = self.current_category["id"]
        self._show_wl_status(f"Weryfikacja i dodawanie '{ticker}'...", is_error=False)

        def _add():
            return self.api.add_ticker(cat_id, ticker)

        def _on_success(item):
            self.input_ticker.clear()
            self._show_wl_status(f"Dodano ticker '{item['ticker']}' do watchlisty.", is_error=False)
            self.load_watchlists(select_category_id=cat_id, select_ticker=item["ticker"])

        def _on_error(err_msg):
            self._show_wl_status(f"Błąd dodawania tickera: {err_msg}", is_error=True)

        run_in_background(_add, on_success=_on_success, on_error=_on_error)

    def _on_quick_add_to_watchlist(self):
        ticker = self.combo_ticker.currentText().strip().upper()
        if not ticker:
            return
        if not self.current_category:
            self._show_wl_status("Najpierw wybierz kategorię po lewej stronie.", is_error=True)
            return

        cat_id = self.current_category["id"]
        self._show_wl_status(f"Dodawanie '{ticker}' do bieżącej kategorii...", is_error=False)

        def _add():
            return self.api.add_ticker(cat_id, ticker)

        def _on_success(item):
            self._show_wl_status(f"Dodano '{item['ticker']}' do '{self.current_category['name']}'.", is_error=False)
            self.load_watchlists(select_category_id=cat_id, select_ticker=item["ticker"])

        def _on_error(err_msg):
            self._show_wl_status(f"Błąd: {err_msg}", is_error=True)

        run_in_background(_add, on_success=_on_success, on_error=_on_error)

    def _on_remove_ticker(self):
        current_item = self.list_tickers.currentItem()
        if not current_item or not self.current_category:
            self._show_wl_status("Wybierz ticker z listy do usunięcia.", is_error=True)
            return

        ticker = current_item.data(Qt.ItemDataRole.UserRole)
        cat_id = self.current_category["id"]

        def _remove():
            return self.api.remove_ticker(cat_id, ticker)

        def _on_success(_):
            self._show_wl_status(f"Usunięto '{ticker}' z watchlisty.", is_error=False)
            self.load_watchlists(select_category_id=cat_id)

        def _on_error(err_msg):
            self._show_wl_status(f"Błąd usuwania tickera: {err_msg}", is_error=True)

        run_in_background(_remove, on_success=_on_success, on_error=_on_error)

    def _on_ticker_item_clicked(self, item: QListWidgetItem):
        ticker = item.data(Qt.ItemDataRole.UserRole)
        if ticker:
            self.combo_ticker.setCurrentText(ticker)

    def _on_ticker_selection_changed(self, text: str):
        ticker = text.strip().upper()
        if ticker and ticker != self.current_ticker:
            self.current_ticker = ticker
            self.load_candles()

    def _on_chart_params_changed(self, _):
        if self.current_ticker:
            self.load_candles()

    def load_candles(self):
        ticker = self.combo_ticker.currentText().strip().upper()
        if not ticker:
            self.chart.show_message("Wybierz lub wpisz symbol tickera.")
            self.lbl_chart_status.setText("")
            return

        interval = self.combo_interval.currentText()
        period = self.combo_period.currentText()

        self.chart.show_message(f"Pobieranie danych rynkowych dla {ticker} ({interval}, {period})...")
        self.lbl_chart_status.setText(f"Pobieranie świec dla {ticker}...")

        def _fetch():
            return self.api.get_candles(ticker=ticker, interval=interval, period=period)

        def _on_success(candle_series):
            count = candle_series.get("count", 0)
            self.chart.set_candle_data(candle_series)
            self.lbl_chart_status.setText(
                f"Pobrano {count} świec dla {ticker} (interwał: {interval}, okres: {period})."
            )

        def _on_error(err_msg):
            self.chart.show_message(f"Nie udało się załadować danych dla {ticker}.\n{err_msg}")
            self.lbl_chart_status.setText(f"Błąd: {err_msg}")

        run_in_background(_fetch, on_success=_on_success, on_error=_on_error)

    def _show_wl_status(self, text: str, is_error: bool = False):
        style = STATUS_ERROR_STYLE if is_error else STATUS_SUCCESS_STYLE
        self.lbl_wl_status.setStyleSheet(style)
        self.lbl_wl_status.setText(text)

    def _on_logout_clicked(self):
        reply = QMessageBox.question(
            self,
            "Wylogowanie",
            "Czy na pewno chcesz się wylogować?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
