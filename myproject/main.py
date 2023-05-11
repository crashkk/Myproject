import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication,QMainWindow, QWidget
from functools import partial
from model_selectGUI import Ui_modelselect 
from classify import *
from BasicSlotfun import *
from menuGUI import Ui_SSDDtool
from mainclassify_GUI import Ui_Form
class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_SSDDtool()
        self.ui.setupUi(self)
        self.childrenwindows={2:ModelSelectWindow}
        self.selectwindow=0#0 is default
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_2.clicked.connect(self.open_next_window)
        self.ui.pushButton.clicked.connect(self.quitstate)
        #control radiobuttons
        self.ui.radioButton_2.clicked.connect(partial(self.winselect,2))
    def quitstate(self):#set the quit button
        app.quit()
    def open_next_window(self):
        self.window2.show()
        self.hide()#hide itself and preserve the innitial state
    def winselect(self,mode):
        current_button=self.sender()#find out the button which has sent the signal
        if current_button.isChecked()==True:
            self.window2=self.childrenwindows[mode](self)#mode==2 means that the program enter the model select state ,while 1 for training process
            self.selectwindow=mode
            self.ui.pushButton_2.setEnabled(True)
        else:
            return
class ModelSelectWindow(QMainWindow):
    def __init__(self,parent=None):
        super(ModelSelectWindow,self).__init__(parent)
        self.ui=Ui_modelselect()
        self.ui.setupUi(self)
        self.parent=parent
        self.ui.pushButton_2.clicked.connect(self.open_next_window)
        self.ui.pushButton.clicked.connect(self.back_to_parent_page)
        self.ui.pushButton_3.clicked.connect(self.quitstate)
        self.ui.pushButton_4.clicked.connect(self.select_model)
    def quitstate(self):#set the quit button
        app.quit()
    def back_to_parent_page(self):
        self.parent.show()
        self.close()
    def open_next_window(self):
        if self.ui.lineEdit_2.text()=='':
            QMessageBox.warning(self, ' Warning', 'Content cannot be empty !')
            return
        if int(self.ui.lineEdit_2.text())<=0:
            QMessageBox.warning(self, ' Warning', 'Timesteps must be positive !')
            return
        self.window2=MainClassifyWindow(self)
        self.window2.show()
        self.hide()#隐藏自己，以保留初始界面状态
    def select_model(self):
        the_image_url=QtWidgets.QFileDialog.getOpenFileName(self,'select your model:','','')
        url=the_image_url
        self.ui.modelselectedpath=str(url[0])
        self.ui.lineEdit.setText(QtCore.QCoreApplication.translate('MainWindow','路径:'+url[0]))

class MainClassifyWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MainClassifyWindow,self).__init__(parent)
        self.ui=Ui_Form()
        self.ui.setupUi(self)
        self.parent=parent
        self.ui.timesteps=self.parent.ui.timesteps
        self.ui.pushButton_2.setEnabled(False)
        if self.parent.ui.modelselectedpath!=None:
            self.ui.current_model=self.parent.ui.modelselectedpath
        self.ui.pushButton.clicked.connect(self.From_files)
        self.ui.pushButton_2.clicked.connect(partial(execute_classify,self.ui))
        self.ui.pushButton_6.clicked.connect(self.quitstate)
        self.ui.pushButton_5.clicked.connect(self.back_to_parent_page)
        self.ui.pushButton_3.clicked.connect(partial(camerashot,self.ui))#turn on camera/continue
        self.ui.pushButton_4.clicked.connect(partial(stopcap_saveimg,self.ui))#send signal to stop capture/pause
    def quitstate(self):#set the quit button
        app.quit()
    def back_to_parent_page(self):
        self.parent.show()
        self.close()
    def From_files(self):
        self.ui.single_classifymode=1
        self.ui.pushButton_2.setEnabled(True)
        the_image_url=QtWidgets.QFileDialog.getOpenFileName(self,'select the steel image\'s path','','')
        url=the_image_url
        self.ui.imagepathsave=str(url[0])
        self.ui.lineEdit.setText(QtCore.QCoreApplication.translate('MainWindow','路径:'+url[0]))

        pixmap=QPixmap(str(url[0]))

        pixmap_item=QGraphicsPixmapItem(pixmap)
        pixmap_item.setScale(7)
        self.ui.graphicsScene.addItem(pixmap_item)
        self.ui.graphicsView.setScene(self.ui.graphicsScene)
if __name__ == '__main__':
    app=QApplication(sys.argv)
    menuWindow=MenuWindow()
    menuWindow.show()
    sys.exit(app.exec_())
