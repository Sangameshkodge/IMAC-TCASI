#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 01:18:42 2019

@author: skodge
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torchvision import datasets, transforms
from LeNet import lenet
import numpy
#import sys
cuda = True
train_batch_size = 32
test_batch_size = 128

best_loss = float("inf")
best_epoch = -1
best_correct=0
dataset_path = './MNIST'

cuda = cuda and torch.cuda.is_available()
trainset = datasets.MNIST(root=dataset_path, train=True, download=True)
train_mean = (((trainset.data.float()).mean()/255).view(1,)).numpy()  # [0.1307]
train_std = (((trainset.data.float()).std()/255).view(1,)).numpy()  # [0.3081]

transform_train = transforms.Compose([
    transforms.RandomCrop(28, padding=4),
    transforms.ToTensor(),
    transforms.Normalize(train_mean, train_std),
])
#sys.exit()
transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(train_mean, train_std),
])
kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}
train_loader = torch.utils.data.DataLoader(datasets.MNIST(
    root=dataset_path, train=True, download=True,
    transform=transform_train),
    batch_size=train_batch_size, shuffle=True, **kwargs)
test_loader = torch.utils.data.DataLoader(
    datasets.MNIST(root=dataset_path, train=False, download=True,
    transform=transform_test),
    batch_size=test_batch_size, shuffle=False, **kwargs)
    
model = lenet(input_size=1,bit_W=4,bit_A=4,sigma=0.6)
if cuda:
    model.cuda()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.MultiStepLR(
    optimizer, milestones=[20,50,80], gamma=0.1)

def train(epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        if cuda:
            data, target = data.cuda(), target.cuda()
        data, target = Variable(data), Variable(target)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % 200 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.data.item()))
            
def test(epoch, best_loss, best_epoch, best_correct, do_quantise,do_add_var,mode,update=False):
    model.eval()
    test_loss = 0
    correct = 0
    for batch_idx, (data, target) in enumerate(test_loader):
        if cuda:
            data, target = data.cuda(), target.cuda()
        data, target = Variable(data), Variable(target)
        output = model.inference(data, do_quantise= do_quantise, do_add_var= do_add_var)
        #output = model(data, training = False)
        # sum up batch loss
        test_loss += criterion(output, target).data.item()
        # get the index of the max log-probability
        pred = output.data.max(1, keepdim=True)[1]
        correct += pred.eq(target.data.view_as(pred)).long().cpu().sum()
        if (batch_idx % 30 == 0 and do_add_var==True):
            print('Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'.format(
                    test_loss, correct, batch_idx*test_batch_size+test_batch_size, 100. * correct /
                    (batch_idx*test_batch_size+test_batch_size)))
        

    test_loss /= len(test_loader.dataset)
    print(
        'Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n\n'.format(
            test_loss, correct, best_correct, 100. * correct /
            len(test_loader.dataset)))
    
    if (best_correct<correct):
        best_epoch = epoch
        best_loss = test_loss
        best_correct=correct
        if (update):
            torch.save(model, "lenet_parameter.pt")
            
    return best_loss, best_epoch, best_correct,correct

print ("Full precision inference:")
epoch=0
model=torch.load("lenet_parameter_noinf.pt")
best_loss, best_epoch, best_correct,_ = test(epoch, best_loss, best_epoch, best_correct, do_quantise=False,do_add_var=False,mode=False,update=False)

print ("Quantised(W-4bit Vin-4bit) inference without error:")
model=torch.load("lenet_parameter_noinf.pt")
model.quantise_weight_flag= False
model.sigma=0.0
model.bit_A=5
model.bit_W=5
model.noofacc=10
model.error_initialiser()
best_loss, best_epoch, best_correct,_ = test(epoch, best_loss, best_epoch, best_correct, do_quantise=True,do_add_var=False,mode=True,update=False)

Min=10000
Max=0
MC_correct=torch.zeros(1000)
for i in range(1000):
    
    correct=0
    model=torch.load("lenet_parameter_noinf.pt")
    model.quantise_weight_flag= False
    model.sigma=0.6
    model.bit_A=5
    model.bit_W=5
    model.error_initialiser()
    model.noofacc=10
    print ("Quantised(W-4bit Vin-4bit) inference{} with error addition:".format(i+1))
    best_loss, best_epoch, _,correct = test(epoch, best_loss, best_epoch, best_correct, do_quantise=True,do_add_var=True,mode=True,update=False)
    MC_correct[i]=correct
    if(correct>Max):
        Max=correct
    if(correct<Min):
        Min=correct
    print(MC_correct[0:i+1].min(),MC_correct[0:i+1].max(),MC_correct[0:i+1].mean(),MC_correct[0:i+1].std())
torch.save(MC_correct, "error_accuracy.pt")
