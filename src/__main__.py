import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
#from .gui import MainWindow
from . import gui

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    gui.setApp(app)
    mw = gui.MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()