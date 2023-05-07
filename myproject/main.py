import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from functools import partial
from classify_GUI import Ui_Form
from classify import *

class NewMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Form()
        self.ui.setupUi(self)
        self.ui.pathbutton.clicked.connect(self.ui.From_files)
        self.ui.classificationsig.clicked.connect(partial(execute_classify,self.ui))
        

if __name__ == '__main__':
    app=QApplication(sys.argv)
    MainWindow=NewMainWindow()
    MainWindow.show()
    sys.exit(app.exec_())