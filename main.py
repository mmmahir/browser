import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QStatusBar, QToolBar, QTabWidget
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from pytablericons import TablerIcons, OutlineIcon

from source.toolbar import newTab, backButton, fowardButton, reloadButton, homeButton


class WebView(QWebEngineView):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def createWindow(self, window_type):
        if window_type in (
            QWebEnginePage.WebWindowType.WebBrowserTab,
            QWebEnginePage.WebWindowType.WebBrowserBackgroundTab,
            QWebEnginePage.WebWindowType.WebBrowserWindow,
        ):
            return self.main_window.add_new_tab(switch_to=True)
        return super().createWindow(window_type)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carbon")
        self.setWindowIcon(QIcon(TablerIcons.load(OutlineIcon.ATOM, color="#ffffff").toqpixmap()))
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        toolbar = QToolBar("Navigation")
        self.addToolBar(toolbar)

        toolbar.addAction(newTab(self))

        toolbar.addAction(backButton(self))

        toolbar.addAction(fowardButton(self))

        toolbar.addAction(reloadButton(self))

        toolbar.addAction(homeButton(self))

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        self.setStatusBar(QStatusBar(self))
        self.add_new_tab(QUrl("https://www.google.com"), "Home")

    def current_browser(self):
        return self.tabs.currentWidget()

    def add_new_tab(self, qurl=None, label="New Tab", switch_to=True):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = WebView(self)
        browser.setUrl(qurl)

        index = self.tabs.addTab(browser, label)
        if switch_to:
            self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda url, browser=browser: self.update_url(url, browser))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser, title))
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
            self.tabs.setTabText(index, title[:18] if title else "New Tab")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec())