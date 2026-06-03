import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow, QStatusBar, QToolBar, QTabWidget
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from pytablericons import TablerIcons, OutlineIcon

def newTab(self):
    new_tab_action = QAction("New Tab", self)
    new_tab_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.PLUS, color="#ffffff").toqpixmap()))
    new_tab_action.triggered.connect(lambda: self.add_new_tab())
    return new_tab_action

def backButton(self):
    back_action = QAction("Back", self)
    back_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.ARROW_NARROW_LEFT, color="#ffffff").toqpixmap()))
    back_action.triggered.connect(lambda: self.current_browser().back())
    return back_action

def fowardButton(self):
    forward_action = QAction("Forward", self)
    forward_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.ARROW_NARROW_RIGHT, color="#ffffff").toqpixmap()))
    forward_action.triggered.connect(lambda: self.current_browser().forward())
    return forward_action

def reloadButton(self):
    reload_action = QAction("Reload", self)
    reload_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.RELOAD, color="#ffffff").toqpixmap()))
    reload_action.triggered.connect(lambda: self.current_browser().reload())
    return reload_action

def homeButton(self):
    home_action = QAction("Home", self)
    home_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.HOME, color="#ffffff").toqpixmap()))
    home_action.triggered.connect(self.go_home)
    return home_action