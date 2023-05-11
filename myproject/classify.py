from PIL import Image
import numpy as np
import torch
from ast import arg
import torch
torch.cuda.current_device()
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os
from torchvision import datasets, transforms
from spiking_model.stbp_model import *
from torchvision.transforms import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import QMessageBox

def execute_classify(ui):#生成输入图像数据
    defects_type={
        0:'cr',
        1:'gg',
        2:'in',
        3:'pa',
        4:'ps',
        5:'rp',
        6:'rs',
        7:'sc',
        8:'sp',
    }
    if ui.single_classifymode==1:#选择路径加载图片
        image=Image.open(ui.imagepathsave)
        image = image.convert('L') # 转换为灰度图
        image = np.array(image, dtype=np.uint8) # 转换为numpy数组，数据类型为uint8
        image=np.array(image)
    elif ui.single_classifymode==2:#选择摄像头读取图片
        image=ui.image
    
    transform=Compose([
        ToTensor(),
        Normalize(0.5,0.5),
    ])

    input=transform(image)
    input=input.unsqueeze(0)

    use_cuda=torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    model = SCNN(ui.timesteps).to(device)
    if ui.current_model!=None:#use personal model
        model.load_state_dict(torch.load(ui.current_model),False)
    else:#use default model
        model.load_state_dict(torch.load('par/SCNN_NEU_CLS_64_target_model.pt'),False)
    input=input.to(device)
    
    output=model(input)
    softmax_output=torch.nn.functional.softmax(output,dim=1)
    ans=output.argmax(dim=1,keepdim=True).item()
    s_ans=softmax_output.max(dim=1)[0].item()
    ui.lcdNumber.display(ans)
    if s_ans<0.2:#the confidence is smaller than the given threshold
        ui.textBrowser.setPlainText('Attention!The confidence is {:.5f} which is smaller than the given threshold,please assure that this is a steel defect image or identify this image manually.'.format(s_ans))
    else:
        ui.textBrowser.setPlainText('The defect type is '+defects_type[int(ans)])
    ui.single_classifymode=0#完成分类任务，模式切换为0
    ui.pushButton_2.setEnabled(False)
