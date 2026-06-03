import sys
from PyQt6.QtCore import (
    QUrl, Qt, QPropertyAnimation, QEasingCurve,
    QSize, QRect, QPoint, pyqtProperty, QTimer
)
from PyQt6.QtGui import (
    QAction, QIcon, QColor, QPainter, QPainterPath,
    QFont, QFontMetrics, QPen
)
from PyQt6.QtWidgets import (
    QApplication, QLineEdit, QMainWindow, QStatusBar,
    QToolBar, QTabWidget, QTabBar, QWidget, QAbstractButton
)
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from pytablericons import TablerIcons, OutlineIcon

from source.toolbar import newTab, backButton, fowardButton, reloadButton, homeButton

APP_STYLE = """
/* ── Global ─────────────────────────────────────────────── */
QMainWindow, QWidget {
    background-color: #0e0e0e;
    color: #d4d4d4;
    font-family: "SF Pro Display", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

/* ── Toolbar ─────────────────────────────────────────────── */
QToolBar {
    background-color: #111111;
    border: none;
    border-bottom: 1px solid #1c1c1c;
    padding: 4px 8px;
    spacing: 2px;
}

QToolBar::separator {
    background: #2a2a2a;
    width: 1px;
    margin: 6px 4px;
}

/* ── Toolbar Buttons ─────────────────────────────────────── */
QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 5px 6px;
    color: #9a9a9a;
}
QToolButton:hover {
    background-color: #1e1e1e;
    color: #f0f0f0;
}
QToolButton:pressed {
    background-color: #cc2a2a;
    color: #ffffff;
}
QToolButton:disabled {
    color: #3a3a3a;
}

/* ── URL Bar ─────────────────────────────────────────────── */
QLineEdit {
    background-color: #181818;
    color: #e8e8e8;
    border: 1px solid #242424;
    border-radius: 8px;
    padding: 5px 14px;
    font-size: 13px;
    selection-background-color: #cc2a2a;
    selection-color: #ffffff;
    min-height: 22px;
}
QLineEdit:focus {
    border: 1px solid #cc2a2a;
    background-color: #1e1e1e;
}
QLineEdit:hover {
    border: 1px solid #333333;
}

/* ── Tab Widget / Pane ───────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background-color: #0e0e0e;
}
QTabWidget::tab-bar {
    alignment: left;
}

/* ── Status Bar ──────────────────────────────────────────── */
QStatusBar {
    background-color: #0a0a0a;
    color: #555555;
    border-top: 1px solid #1a1a1a;
    font-size: 11px;
    padding: 0px 8px;
    min-height: 20px;
}
QStatusBar::item { border: none; }

/* ── Scrollbars ──────────────────────────────────────────── */
QScrollBar:vertical {
    background: #111111; width: 8px; border: none;
}
QScrollBar::handle:vertical {
    background: #2e2e2e; border-radius: 4px; min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #cc2a2a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

QScrollBar:horizontal {
    background: #111111; height: 8px; border: none;
}
QScrollBar::handle:horizontal {
    background: #2e2e2e; border-radius: 4px; min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #cc2a2a; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

/* ── Context Menus ───────────────────────────────────────── */
QMenu {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 4px;
    color: #d4d4d4;
}
QMenu::item { padding: 6px 24px 6px 12px; border-radius: 5px; }
QMenu::item:selected { background-color: #cc2a2a; color: #ffffff; }
QMenu::separator { height: 1px; background: #2a2a2a; margin: 4px 8px; }

/* ── Tooltips ────────────────────────────────────────────── */
QToolTip {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #2e2e2e;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 12px;
}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Animated tab widget content — fades in when a tab is selected
# ─────────────────────────────────────────────────────────────────────────────
class AnimatedWebView(QWebEngineView):
    """WebView that can animate its opacity for open/close effects."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._opacity = 1.0

    # Qt property so QPropertyAnimation can drive it
    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)   # works on top-level; for embedded we use effect below

    opacity = pyqtProperty(float, _get_opacity, _set_opacity)

    def createWindow(self, window_type):
        if window_type in (
            QWebEnginePage.WebWindowType.WebBrowserTab,
            QWebEnginePage.WebWindowType.WebBrowserBackgroundTab,
            QWebEnginePage.WebWindowType.WebBrowserWindow,
        ):
            return self.main_window.add_new_tab(switch_to=True)
        return super().createWindow(window_type)


# ─────────────────────────────────────────────────────────────────────────────
#  Custom tab bar — drawn entirely by hand for full control
# ─────────────────────────────────────────────────────────────────────────────
class CarbonTabBar(QTabBar):
    TAB_H        = 36          # tab strip height
    TAB_MIN_W    = 110
    TAB_MAX_W    = 210
    RADIUS       = 8           # top-corner radius
    ADD_BTN_W    = 32          # width of the "+" button slot

    # colours
    C_BG         = QColor("#0d0d0d")   # bar background
    C_TAB_IDLE   = QColor("#141414")
    C_TAB_HOV    = QColor("#1c1c1c")
    C_TAB_SEL    = QColor("#0e0e0e")
    C_ACCENT     = QColor("#cc2a2a")
    C_TEXT_IDLE  = QColor("#666666")
    C_TEXT_HOV   = QColor("#aaaaaa")
    C_TEXT_SEL   = QColor("#f0f0f0")
    C_CLOSE_HOV  = QColor("#cc2a2a")
    C_SEP        = QColor("#1f1f1f")
    C_ADD        = QColor("#444444")
    C_ADD_HOV    = QColor("#cc2a2a")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setExpanding(False)
        self.setDrawBase(False)
        self.setMouseTracking(True)
        self._hovered_tab   = -1
        self._hovered_close = -1
        self._add_hovered   = False
        self._add_pressed   = False
        self._on_new_tab    = None          # callback set by Browser

        # per-tab animation state  {index: 0.0..1.0}
        self._tab_anim: dict[int, float] = {}
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)    # ~60 fps
        self._anim_timer.timeout.connect(self._tick_animations)

    # ── sizing ────────────────────────────────────────────────
    def tabSizeHint(self, index):
        count = self.count()
        avail = self.width() - self.ADD_BTN_W - 2
        w = max(self.TAB_MIN_W, min(self.TAB_MAX_W, avail // max(count, 1)))
        return QSize(w, self.TAB_H)

    def minimumTabSizeHint(self, index):
        return QSize(self.TAB_MIN_W, self.TAB_H)

    def sizeHint(self):
        w = self.tabRect(self.count() - 1).right() + self.ADD_BTN_W + 4 if self.count() else self.ADD_BTN_W + 4
        return QSize(w, self.TAB_H)

    # ── animation bookkeeping ─────────────────────────────────
    def start_open_anim(self, index):
        self._tab_anim[index] = 0.0
        if not self._anim_timer.isActive():
            self._anim_timer.start()

    def start_close_anim(self, index, callback):
        """
        Animate tab closing: shrink over ~150 ms, then call callback.
        We don't actually delay the remove because QTabBar handles that;
        instead we just do a quick repaint burst for the open direction.
        """
        # For close we simply call callback immediately — PyQt doesn't
        # allow us to intercept QTabBar's own removal cleanly.
        callback()

    def _tick_animations(self):
        done = []
        step = 0.08
        for idx in list(self._tab_anim):
            self._tab_anim[idx] = min(1.0, self._tab_anim[idx] + step)
            if self._tab_anim[idx] >= 1.0:
                done.append(idx)
        for idx in done:
            del self._tab_anim[idx]
        self.update()
        if not self._tab_anim:
            self._anim_timer.stop()

    def _ease_out_cubic(self, t):
        t -= 1
        return t * t * t + 1

    # ── add-button rect ───────────────────────────────────────
    def _add_btn_rect(self):
        last = self.tabRect(self.count() - 1) if self.count() else QRect(0, 0, 0, self.TAB_H)
        x = last.right() + 4
        return QRect(x, (self.TAB_H - 24) // 2, 24, 24)

    # ── painting ──────────────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # background strip
        p.fillRect(self.rect(), self.C_BG)

        # draw each tab (idle/hovered/selected)
        for i in range(self.count()):
            self._draw_tab(p, i)

        # draw "+" button
        self._draw_add(p)
        p.end()

    def _draw_tab(self, p, i):
        rect  = self.tabRect(i)
        sel   = (i == self.currentIndex())
        hov   = (i == self._hovered_tab and not sel)

        # animation scale — new tabs grow in from 0.6 → 1.0 width
        anim_t = self._tab_anim.get(i, 1.0)
        if anim_t < 1.0:
            t = self._ease_out_cubic(anim_t)
            scale = 0.6 + 0.4 * t
            center = rect.center().x()
            w2 = int(rect.width() * scale / 2)
            rect = QRect(center - w2, rect.y(), w2 * 2, rect.height())

        # tab body
        bg = self.C_TAB_SEL if sel else (self.C_TAB_HOV if hov else self.C_TAB_IDLE)

        path = QPainterPath()
        r = float(self.RADIUS)
        path.moveTo(rect.left(), rect.bottom())
        path.lineTo(rect.left(), rect.top() + r)
        path.quadTo(rect.left(), rect.top(), rect.left() + r, rect.top())
        path.lineTo(rect.right() - r, rect.top())
        path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + r)
        path.lineTo(rect.right(), rect.bottom())
        path.closeSubpath()

        p.fillPath(path, bg)

        # red accent bar on selected
        if sel:
            p.fillRect(rect.left() + 8, rect.bottom() - 2, rect.width() - 16, 2, self.C_ACCENT)

        # separator on right edge of idle tabs
        if not sel and i != self.currentIndex() - 1:
            p.setPen(QPen(self.C_SEP, 1))
            p.drawLine(rect.right(), rect.top() + 6, rect.right(), rect.bottom() - 6)

        # label — leave room for the close button on the right
        text_rect = rect.adjusted(10, 0, -30, 0)
        text_color = self.C_TEXT_SEL if sel else (self.C_TEXT_HOV if hov else self.C_TEXT_IDLE)
        p.setPen(text_color)
        font = QFont("SF Pro Display", 11) if sel else QFont("SF Pro Display", 11)
        font.setWeight(QFont.Weight.Medium if sel else QFont.Weight.Normal)
        p.setFont(font)
        fm   = QFontMetrics(font)
        text = fm.elidedText(self.tabText(i), Qt.TextElideMode.ElideRight, text_rect.width())
        p.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)

        # close button (×) — must match _close_rect_for exactly
        close_rect = self._close_rect_for(i)
        if i == self._hovered_close:
            p.setBrush(self.C_CLOSE_HOV)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(close_rect, 4, 4)
            p.setPen(QColor("#ffffff"))
        else:
            p.setPen(QColor("#555555") if (sel or hov) else QColor("#2e2e2e"))

        # draw × symbol
        m = 5
        p.drawLine(close_rect.left() + m,     close_rect.top() + m,
                   close_rect.right() - m,    close_rect.bottom() - m)
        p.drawLine(close_rect.right() - m,    close_rect.top() + m,
                   close_rect.left() + m,     close_rect.bottom() - m)

    def _draw_add(self, p):
        r = self._add_btn_rect()
        if self._add_hovered:
            p.setBrush(QColor("#1e1e1e"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(r, 6, 6)
        color = self.C_ADD_HOV if self._add_hovered else self.C_ADD
        pen = QPen(color, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        cx, cy = r.center().x(), r.center().y()
        half = 6
        p.drawLine(cx - half, cy, cx + half, cy)
        p.drawLine(cx, cy - half, cx, cy + half)

    # ── mouse events ──────────────────────────────────────────
    def _close_rect_for(self, i):
        """Single source of truth for the close button rect (paint + hit-test)."""
        rect = self.tabRect(i)
        size = 18
        x = rect.right() - size - 6
        y = rect.top() + (rect.height() - size) // 2
        return QRect(x, y, size, size)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        prev_tab   = self._hovered_tab
        prev_close = self._hovered_close
        prev_add   = self._add_hovered

        self._hovered_tab   = self.tabAt(pos)
        self._hovered_close = -1
        self._add_hovered   = self._add_btn_rect().contains(pos)

        if self._hovered_tab >= 0:
            if self._close_rect_for(self._hovered_tab).contains(pos):
                self._hovered_close = self._hovered_tab

        if (self._hovered_tab != prev_tab or
                self._hovered_close != prev_close or
                self._add_hovered != prev_add):
            self.update()

    def mousePressEvent(self, event):
        pos = event.pos()
        if self._add_btn_rect().contains(pos):
            self._add_pressed = True
            self.update()
            if self._on_new_tab:
                self._on_new_tab()
            return
        # close button
        for i in range(self.count()):
            if self._close_rect_for(i).contains(pos):
                self.tabCloseRequested.emit(i)
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._add_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self._hovered_tab   = -1
        self._hovered_close = -1
        self._add_hovered   = False
        self.update()


# ─────────────────────────────────────────────────────────────────────────────
#  Custom QTabWidget that uses CarbonTabBar
# ─────────────────────────────────────────────────────────────────────────────
class CarbonTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bar = CarbonTabBar(self)
        self.setTabBar(self._bar)
        self.setDocumentMode(True)
        self.setTabsClosable(False)   # we paint our own close buttons

    def carbon_bar(self):
        return self._bar


# ─────────────────────────────────────────────────────────────────────────────
#  Main browser window
# ─────────────────────────────────────────────────────────────────────────────
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carbon")
        self.setWindowIcon(QIcon(TablerIcons.load(OutlineIcon.ATOM, color="#cc2a2a").toqpixmap()))
        self.resize(1200, 800)

        self.tabs = CarbonTabWidget()
        # Must connect to the bar directly — QTabWidget only forwards
        # tabCloseRequested when setTabsClosable(True), which we don't use.
        self.tabs.carbon_bar().tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        # wire "+" button in tab bar
        self.tabs.carbon_bar()._on_new_tab = lambda: self.add_new_tab()

        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(newTab(self))
        toolbar.addAction(backButton(self))
        toolbar.addAction(fowardButton(self))
        toolbar.addAction(reloadButton(self))
        toolbar.addAction(homeButton(self))

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        self.setStatusBar(QStatusBar(self))
        self.add_new_tab(QUrl("https://www.google.com"), "Home")

    # ── helpers ───────────────────────────────────────────────
    def current_browser(self):
        return self.tabs.currentWidget()

    def add_new_tab(self, qurl=None, label="New Tab", switch_to=True):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = AnimatedWebView(self)
        browser.setUrl(qurl)

        index = self.tabs.addTab(browser, label)

        # kick off open animation
        self.tabs.carbon_bar().start_open_anim(index)

        if switch_to:
            self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda url, b=browser: self.update_url(url, b))
        browser.titleChanged.connect(lambda title, b=browser: self.update_tab_title(b, title))
        return browser

    def close_current_tab(self, index):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(index)

    def current_tab_changed(self, index):
        browser = self.tabs.widget(index)
        if browser:
            self.url_bar.setText(browser.url().toString())

    def go_home(self):
        self.current_browser().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "://" not in text:
            text = "https://" + text
        self.current_browser().setUrl(QUrl(text))

    def update_url(self, qurl, browser=None):
        if browser == self.current_browser():
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title[:20] if title else "New Tab")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    window = Browser()
    window.show()
    sys.exit(app.exec())