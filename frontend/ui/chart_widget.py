import numpy as np
from datetime import datetime, timedelta

from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import seaborn as sns

_POLISH_MONTHS = {
    1: "Sty", 2: "Lut", 3: "Mar", 4: "Kwi", 5: "Maj", 6: "Cze",
    7: "Lip", 8: "Sie", 9: "Wrz", 10: "Paź", 11: "Lis", 12: "Gru",
}


def _polish_date_formatter(x, _pos=None):
    dt = mdates.num2date(x)
    return f"{_POLISH_MONTHS[dt.month]} {dt.year}"


class StockChartWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._generate_data()

        sns.set_theme(style="darkgrid", palette="muted")
        import matplotlib
        matplotlib.rcParams["font.sans-serif"] = ["Inter", "Segoe UI", "DejaVu Sans"]
        matplotlib.rcParams["font.family"] = "sans-serif"

        self.figure = Figure(facecolor="#2B2D6E", tight_layout=True)
        self.canvas = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(111)
        self._draw_chart()

        self.annotation = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            fontsize=9,
            color="white",
            bbox=dict(boxstyle="round,pad=0.4", fc="#3F51B5", ec="white", alpha=0.95),
            arrowprops=dict(arrowstyle="->", color="white"),
        )
        self.annotation.set_visible(False)

        self.vline = self.ax.axvline(x=self.dates[0], color="white", linewidth=0.7, alpha=0.5, visible=False)

        self.hline = self.ax.axhline(y=self.prices[0], color="white", linewidth=0.7, alpha=0.3, linestyle="--", visible=False)

        self._background = None
        self._last_idx = -1
        self.canvas.draw()
        self._background = self.canvas.copy_from_bbox(self.ax.bbox)

        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.canvas.mpl_connect("draw_event", self._on_draw)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def _generate_data(self):
        np.random.seed(42)
        n_days = 180
        start_date = datetime(2026, 5, 1)
        self.dates = [start_date + timedelta(days=i) for i in range(n_days)]
        self.dates_num = np.array([mdates.date2num(d) for d in self.dates])

        returns = np.random.normal(loc=0.0005, scale=0.012, size=n_days)
        price = 250.0 * np.cumprod(1 + returns)
        self.prices = price

        # Volume
        base_vol = 2_000_000
        self.volumes = (base_vol + np.abs(returns) * 80_000_000 + np.random.randint(0, 500_000, n_days)).astype(int)

    def _draw_chart(self):
        ax = self.ax
        ax.set_facecolor("#1E2057")

        ax.plot(
            self.dates,
            self.prices,
            color="#7986CB",
            linewidth=1.8,
            label="KsięBogCorp (KBC)",
        )

        ax.fill_between(self.dates, self.prices, alpha=0.15, color="#7986CB")

        price_min = self.prices.min()
        price_max = self.prices.max()
        price_range = price_max - price_min
        padding = price_range * 0.4
        ax.set_ylim(price_min - padding, price_max + padding)

        ax.set_title("KsięBogCorp (KBC) – Cena akcji", color="white", fontsize=14, fontweight="bold", pad=12)
        ax.set_ylabel("Cena (PLN)", color="white", fontsize=11)
        ax.set_xlabel("Data", color="white", fontsize=11)

        ax.xaxis.set_major_formatter(mticker.FuncFormatter(_polish_date_formatter))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        self.figure.autofmt_xdate(rotation=30)

        ax.tick_params(colors="white", labelsize=9)
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.grid(color="white", alpha=0.1)

        legend = ax.legend(loc="upper left", fontsize=10, framealpha=0.3)
        for text in legend.get_texts():
            text.set_color("white")

    def _on_draw(self, event):
        self._background = self.canvas.copy_from_bbox(self.ax.bbox)

    def _on_mouse_move(self, event):
        if event.inaxes != self.ax or self._background is None:
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
        vol_val = self.volumes[idx]

        self.annotation.xy = (self.dates_num[idx], price_val)
        if idx >= len(self.dates) // 2:
            self.annotation.set_position((-20, 20))
            self.annotation.set_ha("right")
        else:
            self.annotation.set_position((20, 20))
            self.annotation.set_ha("left")
            
        text = (
            f"Data: {date_val.strftime('%d.%m.%Y')}\n"
            f"Cena: {price_val:,.2f} PLN\n"
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
        self.canvas.restore_region(self._background)
        self.ax.draw_artist(self.vline)
        self.ax.draw_artist(self.hline)
        self.ax.draw_artist(self.annotation)
        self.canvas.blit(self.ax.bbox)