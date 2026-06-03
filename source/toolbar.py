from PyQt6.QtGui import QAction, QIcon
from pytablericons import TablerIcons, OutlineIcon

# Icon color palette
_ICON_DEFAULT = "#888888"
_ICON_ACCENT  = "#cc2a2a"   # used for the "new tab" action to give it presence


def newTab(self):
    new_tab_action = QAction("New Tab", self)
    new_tab_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.PLUS, color=_ICON_ACCENT).toqpixmap()))
    new_tab_action.setToolTip("Open new tab")
    new_tab_action.triggered.connect(lambda: self.add_new_tab())
    return new_tab_action


def backButton(self):
    back_action = QAction("Back", self)
    back_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.ARROW_NARROW_LEFT, color=_ICON_DEFAULT).toqpixmap()))
    back_action.setToolTip("Go back")
    back_action.triggered.connect(lambda: self.current_browser().back())
    return back_action


def fowardButton(self):
    forward_action = QAction("Forward", self)
    forward_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.ARROW_NARROW_RIGHT, color=_ICON_DEFAULT).toqpixmap()))
    forward_action.setToolTip("Go forward")
    forward_action.triggered.connect(lambda: self.current_browser().forward())
    return forward_action


def reloadButton(self):
    reload_action = QAction("Reload", self)
    reload_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.RELOAD, color=_ICON_DEFAULT).toqpixmap()))
    reload_action.setToolTip("Reload page")
    reload_action.triggered.connect(lambda: self.current_browser().reload())
    return reload_action


def homeButton(self):
    home_action = QAction("Home", self)
    home_action.setIcon(QIcon(TablerIcons.load(OutlineIcon.HOME, color=_ICON_DEFAULT).toqpixmap()))
    home_action.setToolTip("Go home")
    home_action.triggered.connect(self.go_home)
    return home_action