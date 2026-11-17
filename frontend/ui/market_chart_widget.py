from datetime import datetime, timezone
import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib
import seaborn as sns


class MarketChartWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        sns.set_theme(style="darkgrid", palette="muted")
        matplotlib.rcParams["font.sans-serif"] = ["Inter", "Segoe UI", "DejaVu Sans"]
        matplotlib.rcParams["font.family"] = "sans-serif"

        self.figure = Figure(facecolor="#2B2D6E", tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.dates = []
        self.dates_num = np.array([])
        self.prices = np.array([])
        self.opens = np.array([])
        self.highs = np.array([])
        self.lows = np.array([])
        self.volumes = np.array([])
        self.ticker = ""
        self.interval = ""
        self.period = ""

        self._background = None
        self._last_idx = -1

        self.annotation = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            fontsize=9,
            color="white",
            bbox=dict(boxstyle="round,pad=0.5", fc="#3F51B5", ec="white", alpha=0.95),
            arrowprops=dict(arrowstyle="->", color="white"),
        )
        self.annotation.set_visible(False)

        self.vline = self.ax.axvline(x=0, color="white", linewidth=0.7, alpha=0.5, visible=False)
        self.hline = self.ax.axhline(y=0, color="white", linewidth=0.7, alpha=0.3, linestyle="--", visible=False)

        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.canvas.mpl_connect("draw_event", self._on_draw)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.show_message("Wybierz akcję z listy, aby wyświetlić wykres.")

    def show_message(self, text: str):
        self.ax.clear()
        self.ax.set_facecolor("#1E2057")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        self.ax.text(
            0.5,
            0.5,
            text,
            color="#C5CAE9",
            fontsize=13,
            ha="center",
            va="center",
            transform=self.ax.transAxes,
        )

        self.dates = []
        self.dates_num = np.array([])
        self.prices = np.array([])
        self._background = None
        self.canvas.draw_idle()

    def set_candle_data(self, candle_series: dict):
        candles = candle_series.get("candles", [])
        if not candles:
            self.show_message("Brak danych świecowych dla wybranego zakresu.")
            return

        self.ticker = candle_series.get("ticker", "")
        self.interval = candle_series.get("interval", "1d")
        self.period = candle_series.get("period", "6mo")

        self.dates = [
            datetime.fromtimestamp(c["timestamp"], tz=timezone.utc).replace(tzinfo=None)
            for c in candles
        ]
        self.dates_num = np.array([mdates.date2num(d) for d in self.dates])
        self.prices = np.array([c["close"] for c in candles], dtype=float)
        self.opens = np.array([c["open"] for c in candles], dtype=float)
        self.highs = np.array([c["high"] for c in candles], dtype=float)
        self.lows = np.array([c["low"] for c in candles], dtype=float)
        self.volumes = np.array([c["volume"] for c in candles], dtype=int)

        self._draw_chart()

    def _draw_chart(self):
        ax = self.ax
        ax.clear()
        ax.set_facecolor("#1E2057")

        ax.plot(
            self.dates,
            self.prices,
            color="#7986CB",
            linewidth=1.8,
            label=f"{self.ticker} (Zamknięcie)",
        )

        ax.fill_between(self.dates, self.prices, alpha=0.15, color="#7986CB")

        price_min = float(self.prices.min())
        price_max = float(self.prices.max())
        price_range = max(price_max - price_min, 0.01)
        padding = price_range * 0.3
        ax.set_ylim(price_min - padding, price_max + padding)

        ax.set_title(
            f"{self.ticker} – Wykres cenowy ({self.interval}, {self.period})",
            color="white",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )
        ax.set_ylabel("Cena", color="white", fontsize=11)
        ax.set_xlabel("Data / Czas", color="white", fontsize=11)

        if self.interval in ("1m", "5m", "15m", "30m", "1h"):
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y"))

        self.figure.autofmt_xdate(rotation=25)

        ax.tick_params(colors="white", labelsize=9)
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(color="white", alpha=0.1)

        legend = ax.legend(loc="upper left", fontsize=10, framealpha=0.3)
        if legend:
            for text in legend.get_texts():
                text.set_color("white")

        self.annotation = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            fontsize=9,
            color="white",
            bbox=dict(boxstyle="round,pad=0.5", fc="#3F51B5", ec="white", alpha=0.95),
            arrowprops=dict(arrowstyle="->", color="white"),
        )
        self.annotation.set_visible(False)

        first_x = self.dates_num[0] if len(self.dates_num) > 0 else 0
        first_y = self.prices[0] if len(self.prices) > 0 else 0
        self.vline = ax.axvline(x=first_x, color="white", linewidth=0.7, alpha=0.5, visible=False)
        self.hline = ax.axhline(y=first_y, color="white", linewidth=0.7, alpha=0.3, linestyle="--", visible=False)

        self._last_idx = -1
        self.canvas.draw()
        self._background = self.canvas.copy_from_bbox(self.ax.bbox)

    def _on_draw(self, event):
        if len(self.prices) > 0:
            self._background = self.canvas.copy_from_bbox(self.ax.bbox)

    def _on_mouse_move(self, event):
        if len(self.prices) == 0 or event.inaxes != self.ax or self._background is None:
            if self.annotation.get_visible():
                self.annotation.set_visible(False)
                self.vline.set_visible(False)
                self.hline.set_visible(False)
                self._restore_and_blit()
            return

        idx = int(np.argmin(np.abs(self.dates_num - event.xdata)))
        if idx == self._last_idx:
            return
        self._last_idx = idx

        date_val = self.dates[idx]
        price_val = self.prices[idx]
        open_val = self.opens[idx]
        high_val = self.highs[idx]
        low_val = self.lows[idx]
        vol_val = self.volumes[idx]

        self.annotation.xy = (self.dates_num[idx], price_val)

        if idx >= len(self.dates) // 2:
            self.annotation.set_position((-20, 20))
            self.annotation.set_ha("right")
        else:
            self.annotation.set_position((20, 20))
            self.annotation.set_ha("left")

        time_str = (
            date_val.strftime("%d.%m.%Y %H:%M")
            if self.interval in ("1m", "5m", "15m", "30m", "1h")
            else date_val.strftime("%d.%m.%Y")
        )

        text = (
            f"Symbol: {self.ticker}\n"
            f"Czas: {time_str}\n"
            f"Zamknięcie: {price_val:,.2f}\n"
            f"Otwarcie: {open_val:,.2f} | Max: {high_val:,.2f} | Min: {low_val:,.2f}\n"
            f"Wolumen: {vol_val:,}"
        )
        self.annotation.set_text(text)
        self.annotation.set_visible(True)

        self.vline.set_xdata([self.dates_num[idx]])
        self.vline.set_visible(True)
        self.hline.set_ydata([price_val])
        self.hline.set_visible(True)

        self._restore_and_blit()

    def _restore_and_blit(self):
        if self._background is None:
            return
        self.canvas.restore_region(self._background)
        self.ax.draw_artist(self.vline)
        self.ax.draw_artist(self.hline)
        self.ax.draw_artist(self.annotation)
        self.canvas.blit(self.ax.bbox)
