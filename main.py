import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QStatusBar, QToolBar
from PyQt6.QtWebEngineWidgets import QWebEngineView


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic PyQt6 Browser")
        self.resize(1200, 800)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

        toolbar = QToolBar("Navigation")
        self.addToolBar(toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        back_action = QAction("Back", self)
        back_action.triggered.connect(self.browser.back)
        toolbar.addAction(back_action)

        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_action)

        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_action)

        home_action = QAction("Home", self)
        home_action.triggered.connect(self.go_home)
        toolbar.addAction(home_action)



        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadFinished.connect(self.update_title)

        self.setStatusBar(QStatusBar(self))

    def go_home(self):
        self.browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "://" not in text:
            text = "https://" + text
        self.browser.setUrl(QUrl(text))

    def update_url(self, qurl):
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)

    def update_title(self):
        self.setWindowTitle("Carbon")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec())