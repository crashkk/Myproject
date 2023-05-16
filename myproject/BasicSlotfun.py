from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from Camera import Camera
import cv2
import numpy as np


def stopcap_saveimg(ui):
    ui.camera.stop_display()
    ui.single_classifymode=2
    ui.pushButton_2.setEnabled(True)

def camerashot(ui):#using camera to generate test image
    ui.pushButton_7.setEnabled(False)
    ui.pushButton_8.setEnabled(False)
    ui.camera=Camera(ui)#实例化摄像头
    ui.camera.start_display()
