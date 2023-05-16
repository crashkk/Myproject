import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication,QMainWindow, QWidget,QTableWidgetItem
from functools import partial
from model_selectGUI import Ui_modelselect 
from classify import *
from BasicSlotfun import *
from menuGUI import Ui_SSDDtool
from mainclassify_GUI import Ui_Form
from loginGUI import Ui_Login
from administratorGUI import Ui_adm
from administratorLoginGUI import Ui_admLogin
from trainGUI import Ui_Train
from settingGUI import Ui_Setting
import pyodbc
from time import sleep
from threading import Thread
from PyQt5.QtCore import pyqtSignal,QObject
import cv2
import numpy as np
import os
class SignalStore(QObject):
    # 定义一种信号
    progress_update = pyqtSignal(int)
    # 还可以定义其他作用的信号

# 实例化
so = SignalStore()

class AdmWindow(QMainWindow):
    def __init__(self,parent=None):
        super(AdmWindow,self).__init__(parent)
        self.ui=Ui_adm()
        self.ui.setupUi(self)
        self.parent=parent
        
        self.cnxn = pyodbc.connect('DRIVER={SQL Server};'' SERVER=localhost;'' DATABASE=Users;'' UID=sa;'' PWD=messino1')
        self.cursor=self.cnxn.cursor()
        self.cursor.execute(f"SELECT COUNT(*) FROM {'users'}")
        self.row_count = self.cursor.fetchone()[0]#获取已注册的用户个数
        self.cursor.execute("SELECT * From users")
        rows = self.cursor.fetchall()
        self.ui.tableWidget.setRowCount(self.row_count)
        self.ui.tableWidget.setColumnCount(2)
        for i in range(self.row_count):
            u=QTableWidgetItem(rows[i][0])
            p=QTableWidgetItem(rows[i][1])
            self.ui.tableWidget.setItem(i,0,u)
            self.ui.tableWidget.setItem(i,1,p)
        
        self.ui.pushButton_6.clicked.connect(self.back_to_parent_page)
        self.ui.pushButton_5.clicked.connect(self.quitstate)

        self.ui.pushButton.clicked.connect(self.add)
        self.ui.pushButton_2.clicked.connect(self.check)
        self.ui.pushButton_3.clicked.connect(self.delete)
        self.ui.pushButton_4.clicked.connect(self.modify)
    def back_to_parent_page(self):
        self.parent.show()
        self.cursor.close()
        self.cnxn.close()
        self.close()
    def quitstate(self):#set the quit button
        app.quit()
    def add(self):
        uname,ok1=QtWidgets.QInputDialog.getText(self,'username:','')
        upssw,ok2=QtWidgets.QInputDialog.getText(self,'password:','')
        if uname or upssw:
            self.cursor.execute('INSERT INTO users (username,password) VALUES(?,?)',uname,upssw)
            self.cnxn.commit()
            QMessageBox.information(self,'Success','Add a new user successfully!')
            self.row_count+=1
            self.ui.tableWidget.setRowCount(self.row_count)
            self.ui.tableWidget.setItem(self.row_count-1,0,QTableWidgetItem(uname))
            self.ui.tableWidget.setItem(self.row_count-1,1,QTableWidgetItem(upssw))
        else:
            QMessageBox.warning(self,'Warning','Fail to add, please check out your input!')
    def check(self):
        uname,ok=QtWidgets.QInputDialog.getText(self,'username:','')
        if not uname:
            QMessageBox.warning(self,'Warning','Fail to check, please check out your input!')
            return
        result=self.cursor.execute('SELECT * FROM users WHERE username=?',uname).fetchone()
        if result:
            QMessageBox.information(self,'Success','Find this user successfully!')
        else:
            QMessageBox.warning(self,'Warning','Cannot find this user!')
    def delete(self):
        uname,ok=QtWidgets.QInputDialog.getText(self,'username:','')
        if not uname:
            QMessageBox.warning(self,'Warning','Fail to delete, please check out your input!')
            return
        check_result=self.cursor.execute('SELECT * FROM users WHERE username=?',uname).fetchone()#首先查看该用户是否存在
        if not check_result:
            QMessageBox.warning(self,'Warning','Cannot find this user! Please check out your input and try again.')
        else:#用户存在，继续下一步删除操作
            self.cursor.execute('DELETE FROM users WHERE username=?',uname)
            self.cnxn.commit()
            self.row_count-=1
            rows = self.cursor.execute("SELECT * From users").fetchall()
            self.ui.tableWidget.setRowCount(self.row_count)
            self.ui.tableWidget.setColumnCount(2)
            for i in range(self.row_count):
                u=QTableWidgetItem(rows[i][0])
                p=QTableWidgetItem(rows[i][1])
                self.ui.tableWidget.setItem(i,0,u)
                self.ui.tableWidget.setItem(i,1,p)
    def modify(self):
        uname,ok=QtWidgets.QInputDialog.getText(self,'Input the user that you want to modify:','')
        if not uname:
            QMessageBox.warning(self,'Warning','Fail to delete, please check out your input!')
            return
        check_result=self.cursor.execute('SELECT * FROM users WHERE username=?',uname).fetchone()#首先查看该用户是否存在
        if not check_result:
            QMessageBox.warning(self,'Warning','Cannot find this user! Please check out your input and try again.')
        else:#用户存在，继续下一步修改操作
            newname,ok=QtWidgets.QInputDialog.getText(self,'new username:','')
            newpssw,ok=QtWidgets.QInputDialog.getText(self,'new password:','')
            if newname and newpssw:
                self.cursor.execute('UPDATE users SET username=?, password=? WHERE username=?',newname,newpssw,uname)
                self.cnxn.commit()
                rows = self.cursor.execute("SELECT * From users").fetchall()
                for i in range(self.row_count):
                    u=QTableWidgetItem(rows[i][0])
                    p=QTableWidgetItem(rows[i][1])
                    self.ui.tableWidget.setItem(i,0,u)
                    self.ui.tableWidget.setItem(i,1,p)
            else:
                QMessageBox.warning(self,'Warning','Information cannot be empty!')
class AdmLoginWindow(QMainWindow):
    def __init__(self,parent=None):
        super(AdmLoginWindow,self).__init__(parent)
        self.ui=Ui_admLogin()
        self.ui.setupUi(self)
        self.parent=parent
        self.ui.pushButton.clicked.connect(self.open_next_window)
        self.ui.pushButton_2.clicked.connect(self.transfer_to_userLogin)
    def open_next_window(self):
        adm=None
        password=None
        adm=self.ui.lineEdit.text()
        password=self.ui.lineEdit_2.text()
        if not adm or not password:
            QMessageBox.warning(self, ' Warning', 'Account or password cannot be empty!')
            return
        cnxn = pyodbc.connect('DRIVER={SQL Server};'' SERVER=localhost;'' DATABASE=Users;'' UID=sa;'' PWD=messino1')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM administrators WHERE administrator=? AND password=?", (adm, password))
        result = cursor.fetchone()
        
        if result:#管理员登录成功
            self.window=AdmWindow(self)
            self.window.show()
            self.hide()#close itself
        else:#用户登录失败
            QMessageBox.warning(self, ' Warning', 'Wrong password or account! Please check out.')
    def transfer_to_userLogin(self):
        self.parent.show()
        self.hide()#hide itself and preserve the innitial state    
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Login()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.open_next_window)
        self.ui.pushButton_2.clicked.connect(self.transfer_to_admLogin)
    def open_next_window(self):
        username=None
        password=None
        username=self.ui.lineEdit.text()
        password=self.ui.lineEdit_2.text()
        if not username or not password:
            QMessageBox.warning(self, ' Warning', 'Account or password cannot be empty!')
            return
        cnxn = pyodbc.connect('DRIVER={SQL Server};'' SERVER=localhost;'' DATABASE=Users;'' UID=sa;'' PWD=messino1')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        
        if result:#用户登录成功
            self.window=MenuWindow(self)
            self.window.show()
            self.hide()#close itself
        else:#用户登录失败
            QMessageBox.warning(self, ' Warning', 'Wrong password or account! Please check out.')
    def transfer_to_admLogin(self):
        self.window2=AdmLoginWindow(self)
        self.window2.show()
        self.hide()#hide itself and preserve the innitial state
class MenuWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MenuWindow,self).__init__(parent)
        self.ui=Ui_SSDDtool()
        self.ui.setupUi(self)
        self.parent=parent
        self.childrenwindows={1:ModelSettingWindow,
                              2:ModelSelectWindow}
        self.selectwindow=0#0 is default
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_2.clicked.connect(self.open_next_window)
        self.ui.pushButton.clicked.connect(self.quitstate)
        self.ui.pushButton_4.clicked.connect(self.back_to_parent_page)
        #control radiobuttons
        self.ui.radioButton_2.clicked.connect(partial(self.winselect,2))
        self.ui.radioButton.clicked.connect(partial(self.winselect,1))
    def quitstate(self):#set the quit button
        app.quit()
    def open_next_window(self):
        self.window2.show()
        self.hide()#hide itself and preserve the innitial state
    def back_to_parent_page(self):
        self.parent.show()
        self.close()
    def winselect(self,mode):
        current_button=self.sender()#find out the button which has sent the signal
        if current_button.isChecked()==True:
            self.window2=self.childrenwindows[mode](self)#mode==2 means that the program enter the model select state ,while 1 for training process
            self.selectwindow=mode
            self.ui.pushButton_2.setEnabled(True)
        else:
            return
class ModelSettingWindow(QMainWindow):
    def __init__(self,parent=None):
        super(ModelSettingWindow,self).__init__(parent)
        self.ui=Ui_Setting()
        self.ui.setupUi(self)
        self.parent=parent
        self.modelsavepath=None
        self.datasetpath=None
        self.ui.pushButton_4.clicked.connect(self.save_model_path)
        self.ui.pushButton_5.clicked.connect(self.dataset_path)
        self.ui.pushButton.clicked.connect(self.back_to_parent_page)
        self.ui.pushButton_3.clicked.connect(self.quitstate)
        self.ui.pushButton_2.clicked.connect(self.configset)
    def quitstate(self):#set the quit button
        app.quit()
    def back_to_parent_page(self):
        self.parent.show()
        self.close()
    def save_model_path(self):
        model_path=QtWidgets.QFileDialog.getExistingDirectory(self, "选择目标文件夹", "/", QtWidgets.QFileDialog.ShowDirsOnly)
        url=model_path
        self.modelsavepath=str(url)
        self.ui.lineEdit.setText(str(url))
    def dataset_path(self):
        d_path=QtWidgets.QFileDialog.getExistingDirectory(self, "选择目标文件夹", "/", QtWidgets.QFileDialog.ShowDirsOnly)
        url=d_path
        self.datasetpath=str(url)
        self.ui.lineEdit_2.setText(str(url))
    def configset(self):
        if not self.ui.lineEdit_4.text() or not self.ui.lineEdit_5.text() or not self.ui.lineEdit_6.text() or not self.modelsavepath or not self.datasetpath:
            QMessageBox.warning(self, ' Warning', 'Content cannot be empty !')
            return
        self.CUDA=bool(self.ui.comboBox.currentText())
        self.workers_num=int(self.ui.spinBox.value())
        self.pin_memory=bool(self.ui.comboBox_2.currentText())
        self.data_size=int(self.ui.lineEdit_4.text())
        self.lr=float(self.ui.lineEdit_5.text())
        self.epoch=int(self.ui.lineEdit_6.text())
        self.data_balance=bool(self.ui.comboBox_3.currentText())
        self.time_steps=int(self.ui.spinBox_2.value())
        self.train_test_split=float(self.ui.doubleSpinBox.value())
        if self.data_size>0 and self.lr>0 and self.epoch>0:
            self.window2=ModelTrainWindow(self)
            self.window2.show()
            self.hide()
        else:
            QMessageBox.warning(self, ' Warning', 'Please input positive value !')
            return
class ModelTrainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(ModelTrainWindow,self).__init__(parent)
        self.ui=Ui_Train()
        self.ui.setupUi(self)
        self.parent=parent
        self.epoch=self.parent.epoch
        self.ongoing=False
        self.ui.progressBar.setRange(0,self.parent.epoch)
        so.progress_update.connect(self.setProgress)
        self.ui.pushButton_2.clicked.connect(self.quitstate)
        self.ui.pushButton.clicked.connect(self.back_to_parent_page)
        self.ui.pushButton_3.clicked.connect(self.progressBar)
    def quitstate(self):#set the quit button
        app.quit()
    def progressBar(self):
        epoch=self.epoch
        def Threadfun(epoch):
            self.ongoing = True
            for i in range(1,epoch+1):
                sleep(10)
                # 设置进度值
                so.progress_update.emit(i)
            self.ongoing = False
            self.ui.pushButton_3.setEnabled(False)
        worker = Thread(target=partial(Threadfun,epoch))
        worker.start()

    def setProgress(self,value):
        self.ui.progressBar.setValue(value)
        if value==self.epoch:
            QMessageBox.information(self, 'Successfully', 'Model has been trained, you can find it with the form of **.pt in your savepath now!')
    def back_to_parent_page(self):
        self.parent.show()
        self.close()
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
        self.ui.pushButton_5.clicked.connect(self.select_results_path)
    def quitstate(self):#set the quit button
        app.quit()
    def back_to_parent_page(self):
        self.parent.show()
        self.close()
    def open_next_window(self):
        if self.ui.lineEdit_2.text()=='' or not self.ui.lineEdit.text() or not self.ui.lineEdit_3.text():
            QMessageBox.warning(self, ' Warning', 'Content cannot be empty !')
            return
        if int(self.ui.lineEdit_2.text())<=0:
            QMessageBox.warning(self, ' Warning', 'Timesteps must be positive !')
            return
        self.window2=MainClassifyWindow(self)
        self.window2.show()
        self.hide()#隐藏自己，以保留初始界面状态
    def select_results_path(self):
        r_path=QtWidgets.QFileDialog.getExistingDirectory(self, "Results saved to:", "/", QtWidgets.QFileDialog.ShowDirsOnly)
        url=r_path
        self.ui.resultssavedpath=str(url)
        self.ui.lineEdit_3.setText(str(url))    
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
        self.results_saved_path=self.parent.ui.resultssavedpath
        self.ui.timesteps=self.parent.ui.timesteps
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_8.setEnabled(False)
        if self.parent.ui.modelselectedpath!=None:
            self.ui.current_model=self.parent.ui.modelselectedpath
        self.ui.pushButton.clicked.connect(self.From_files)
        self.ui.pushButton_2.clicked.connect(partial(execute_classify,self.ui))
        self.ui.pushButton_6.clicked.connect(self.quitstate)
        self.ui.pushButton_5.clicked.connect(self.back_to_parent_page)
        self.ui.pushButton_3.clicked.connect(partial(camerashot,self.ui))#turn on camera/continue
        self.ui.pushButton_4.clicked.connect(partial(stopcap_saveimg,self.ui))#send signal to stop capture/pause
        self.ui.pushButton_7.clicked.connect(self.relabel)
        self.ui.pushButton_8.clicked.connect(self.contribute)
    def quitstate(self):#set the quit button
        app.quit()
    def back_to_parent_page(self):
        self.parent.show()
        self.close()
    def relabel(self):
        relabelname,ok=QtWidgets.QInputDialog.getText(self,'Relabel manually:','')
        if not relabelname:
            QMessageBox.warning(self,'Warning!','Content cannot be empty!')
            return
        else:
            self.ui.label_to_save=relabelname
    def contribute(self):
        save_fig=self.ui.image_to_save
        if not os.path.exists(self.results_saved_path+'/'+self.ui.label_to_save):
            os.makedirs(self.results_saved_path+'/'+self.ui.label_to_save)
        files_in_label=len(os.listdir(self.results_saved_path+'/'+self.ui.label_to_save+'/'))
        ok=cv2.imwrite(self.results_saved_path+'/'+self.ui.label_to_save+'/'+str(files_in_label+1)+'.png',save_fig)
        if ok:
            QMessageBox.information(self,'Successfully!','You have saved a result!')
            return
    def From_files(self):
        self.ui.single_classifymode=1
        self.ui.pushButton_2.setEnabled(True)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_8.setEnabled(False)
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
    loginWindow=LoginWindow()
    loginWindow.show()
    sys.exit(app.exec_())
