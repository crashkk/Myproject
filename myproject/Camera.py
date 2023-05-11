import sys
import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QImage,QPixmap
class Camera():
    def __init__(self,ui):
        self.ui=ui
        self.cap=cv2.VideoCapture(0)

        self.timer=None#计时器
        self.display_started=False#控制暂停

    def start_display(self):
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1)
        self.display_started=True

    def stop_display(self):
        self.timer.stop()
        self.display_started=False

    def update(self):
        ret,frame=self.cap.read()
        if ret:
            frame=cv2.resize(frame,(7*64,7*64))
            gray_image=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            frame2=cv2.resize(gray_image,(64,64))#更新ui中的图像数据，为classify做准备
            self.ui.image=frame2

            h,w=gray_image.shape
            qimage=QImage(gray_image,w,h,w,QImage.Format_Grayscale8)
            pixmap=QPixmap.fromImage(qimage)
            self.ui.graphicsScene.clear()
            self.ui.graphicsScene.addPixmap(pixmap)
            self.ui.graphicsView.setScene(self.ui.graphicsScene)
            