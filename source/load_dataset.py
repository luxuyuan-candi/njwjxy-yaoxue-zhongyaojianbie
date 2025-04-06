import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os
import matplotlib.pyplot as plt
import numpy as np

# 图像预处理（按需修改）
transform = transforms.Compose([
    #transforms.Resize((224, 224)),   # 调整图像大小
    transforms.ToTensor(),           # 转成 Tensor
    transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)  # 简单归一化
])

# 加载数据集
current_dir = os.getcwd()
dataset_path = current_dir + "/dataset/val"  # 替换为你的路径
dataset = datasets.ImageFolder(root=dataset_path, transform=transform)

# 创建 DataLoader
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# 测试输出
for images, labels in dataloader:
    print(images.shape)  # torch.Size([32, 3, 224, 224])
    print(labels.shape)  # torch.Size([32])
    break

print(dataset.class_to_idx)

def imshow(img):
    img = img.numpy().transpose((1, 2, 0))  # CxHxW -> HxWxC
    img = img * 0.5 + 0.5  # 去归一化
    plt.imshow(img)
    plt.axis('off')
    plt.show()

# 显示第一张图
images, labels = next(iter(dataloader))
imshow(images[0])
print("Label:", labels[0].item())