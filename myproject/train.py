import numpy as np
import torch
torch.cuda.current_device()
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import time
import os
from torchvision import datasets, transforms
from data_process import NEU_CLS_64
from spiking_model.stbp_model import SCNN

def model_train(window,target_model, device, optimizer, epoch ,total_train_dataloader):#训练包含被遗忘样本的模型
    target_model.train()
    for batch_idx1, (data, target) in enumerate(total_train_dataloader):
        #target= torch.topk(target, 1)[1].squeeze(1)
        data, target = data.to(device), target.to(device)

        # necessary for general dataset: broadcast input
        #data, _ = torch.broadcast_tensors(data, torch.zeros((steps,) + data.shape)) 
        #data = data.permute(1, 2, 3, 4, 0)

        if epoch==0 and batch_idx1==0:
            output = target_model(data,simulation_required=True)
        else:
            output = target_model(data)
        loss = F.cross_entropy(output, target)
        #loss=criterion(output, target)
        #loss =F.mse_loss(output,target)
        optimizer.zero_grad() 
        loss.backward()
        optimizer.step()
        if batch_idx1 % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tlearning_rate:{:.7f}'.format(
                epoch, batch_idx1 * len(data / window.time_steps), len(total_train_dataloader.dataset),
                    100. * batch_idx1 * len(data / window.time_steps)/ len(total_train_dataloader.dataset), loss.item(),optimizer.state_dict()['param_groups'][0]['lr']))

def test(window,target_model, device, test_loader, epoch):
    target_model.eval()    
    test_loss = 0
    correct = 0
    isEval = False
    label_list=[]
    pred_list=[]

    with torch.no_grad():
        for data, target in test_loader:
            #target= torch.topk(target, 1)[1].squeeze(1)
            data, target = data.to(device), target.to(device)

            if len(label_list)==0:
                label_list=target
            else:
                label_list=torch.cat([label_list,target],dim=0)

            #data, _ = torch.broadcast_tensors(data, torch.zeros((steps,) + data.shape))
            #data = data.permute(1, 2, 3, 4, 0)
            output = target_model(data)
            #test_loss +=criterion(output, target).item()
            test_loss += F.cross_entropy(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

            if len(pred_list)==0:
                pred_list=pred
            else:
                pred_list=torch.cat([pred_list,pred],dim=0)


    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

def train_SCNN(window):
    use_cuda=window.CUDA and torch.cuda.is_available()
    device = torch.device("cuda:0" if use_cuda else "cpu")
    kwargs = {'num_workers': window.workers_num, 'pin_memory': window.pin_memory} if use_cuda else {}
    
    train_dataset=NEU_CLS_64(train=True)
    train_dataset.resample()
    train_dataloader=torch.utils.data.DataLoader(train_dataset,batch_size=25, shuffle=True,**kwargs)
    test_dataset=NEU_CLS_64(train=False)#test dataset don't need to resample
    test_dataloader=torch.utils.data.DataLoader(test_dataset,batch_size=25, shuffle=False,**kwargs)
    
    target_model= SCNN().to(device)#this for shallow snn
    #target_model = nn.DataParallel(target_model,device_ids=[1,2])  #this for parallel training(not suitable for cifar or dvs-cifar)
    optimizer = optim.Adam(target_model.parameters(), lr=window.lr)
    #scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode = 'min', factor = 0.1, patience = 10, verbose = False, threshold = 0.0001, threshold_mode = 'rel', cooldown = 0, min_lr = 0, eps = 1e-08)

    target_model_log_path=window.modelsavepath#经过训练不含被遗忘数据的目标模型参数
    start_time=time.time()
    """
    这一模块进行SNNS的基础训练
    """
    for epoch in range(window.epoch):
        model_train(target_model, device, optimizer,epoch, train_dataloader)#先对选定的总样本进行训练
        test(target_model, device, test_dataloader, epoch)

    torch.save(target_model.state_dict(), window.modelsavepath+ '/personal_model.pt')#存储模型权重参数
    torch.save(target_model, window.modelsavepath+ '/personal_model.pt')#存储模型结构