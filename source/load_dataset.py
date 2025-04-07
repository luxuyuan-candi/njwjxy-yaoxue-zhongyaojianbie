from torchvision import datasets, transforms

class Local_dataset():
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.transform = transforms.Compose([
        #transforms.Resize((224, 224)),   # 调整图像大小
            transforms.ToTensor(),           # 转成 Tensor
            transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)  # 简单归一化
        ])
    def get_dataset(self):
        return datasets.ImageFolder(root=self.dataset_path, transform=self.transform)