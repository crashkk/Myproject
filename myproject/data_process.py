from torch.utils.data import Dataset
import os
from torchvision.io import read_image
from torchvision.transforms import *
import torch
import numpy as np
from PIL import Image
from imblearn.over_sampling import RandomOverSampler,SMOTE
from imblearn.under_sampling import RandomUnderSampler
import random

random_seed_for_NEU64_traintestsplit=8064
regenerate_NEU_64_or_not='N'
def NEU_CLS_64_dataset_make():#randomly split the dataset into train slice or test slice
    root='snn_forget_industry/industry_dataset/NEU_CLS_64/'
    classes={
        'cr':0,
        'gg':1,
        'in':2,
        'pa':3,
        'ps':4,
        'rp':5,
        'rs':6,
        'sc':7,
        'sp':8
    }
    total_data=[]
    total_label=[]
    for cls in os.listdir(root):
        if cls == 'pregenerate_data':
            continue
        cls_path=os.path.join(root,cls)
        for data in os.listdir(cls_path):
            data_path=os.path.join(cls_path,data)

            image=Image.open(data_path)
            image = image.convert('L') # 转换为灰度图
            image = np.array(image, dtype=np.uint8) # 转换为numpy数组，数据类型为uint8
            image=np.array(image)
            
            if len(total_data)==0:
                total_data=np.expand_dims([image],axis=0)
            else:
                total_data=np.concatenate((total_data,np.expand_dims([image],axis=0)))

            total_label.append(classes[cls])#Attention,the label must be corresponding to data!
    total_label=np.array(total_label)
    return total_data,total_label

class NEU_CLS_64(Dataset):
    def __init__(self,train=True,forget_mode=False,generator=NEU_CLS_64_dataset_make):
        self.forget_mode=forget_mode
        if regenerate_NEU_64_or_not=='Y':
            X,y=generator()
            random.seed(random_seed_for_NEU64_traintestsplit)
            pos=list(i for i in range(len(y)))
            random.shuffle(pos)
            split_size=0.8#train test split
            X_train=X[pos[:int(split_size*len(y))]]
            y_train=y[pos[:int(split_size*len(y))]]
            X_test=X[pos[int(split_size*len(y)):]]
            y_test=y[pos[int(split_size*len(y)):]]
            if train==True:
                self.X=X_train
                self.y=y_train
            elif train==False:
                self.X=X_test
                self.y=y_test

        if  train==True:
            transform=Compose([
                ToTensor(),
                #RandomResizedCrop(size=32,scale=(0.7,1)),
                #Resize(128),
                #RandomCrop(32),
                RandomHorizontalFlip(),
                RandomVerticalFlip(),
                RandomRotation(degrees=10),
                Normalize((0.5),(0.5))
            ])
        
        elif train==False:
            transform=Compose([
                ToTensor(),
                #Resize(128),
                Normalize((0.5),(0.5))
            ])

        self.transform=transform
        self.train=train
        #self.resampler=RandomUnderSampler(random_state=678)
        #self.resampler=SMOTE(random_state=678)
        self.resampler=RandomOverSampler(random_state=678)
        
    def __getitem__(self, index):
        x=self.X[index]
        y=self.y[index]

        if self.train==False:
            x=x.reshape(64,64)

        if self.transform:
            x=self.transform(x)

        return x,y

    def __len__(self):
        return len(self.X)
    
    def resample(self,sample=True):#oversample to compensate imbalance of classes of data
        X_slice,y_slice=self.X,self.y

        if sample==False:
            self.X=X_slice.reshape(len(X_slice),64,64)
            self.y=y_slice

        X_slice=X_slice.reshape(len(X_slice),-1)
        X_resampled,y_resampled=self.resampler.fit_resample(X_slice,y_slice)
        X_resampled=X_resampled.reshape(len(X_resampled),64,64)
        self.X=X_resampled
        self.y=y_resampled
        
            

if __name__ == '__main__':
    train_dataset=NEU_CLS_64(train=True)
    train_dataset.resample()
    '''
    train_dataloader=torch.utils.data.DataLoader(train_dataset,batch_size=5,shuffle=True)
    c=[0,0,0,0,0,0,0,0,0]
    for idx,(data,label) in enumerate(train_dataloader):
        print(data.shape,label)
    '''
        
    