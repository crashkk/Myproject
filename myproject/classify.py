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

def execute_classify(ui):#生成输入图像数据
    image=Image.open(ui.imagepathsave)
    image = image.convert('L') # 转换为灰度图
    image = np.array(image, dtype=np.uint8) # 转换为numpy数组，数据类型为uint8
    image=np.array(image)
    
    transform=Compose([
        ToTensor(),
        Normalize(0.5,0.5),
    ])

    input=transform(image)
    input=input.unsqueeze(0)

    use_cuda=torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    model = SCNN().to(device)
    model.load_state_dict(torch.load('par/SCNN_NEU_CLS_64_target_model.pt'),False)
    input=input.to(device)
    
    output=model(input)
    ans=output.argmax(dim=1,keepdim=True).item()
    ui.Output_classresult_2.setText(str(ans))
