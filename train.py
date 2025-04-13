from source.load_dataset import Local_dataset
import os
from torch.utils.data import DataLoader
from torchvision.models import resnet34
import torch.nn as nn
import torch
from torch.utils.tensorboard import SummaryWriter

batch_size = 128
learn_rate = 0.001
num_epochs = 100
log_dir = "runs/exp1"


def main():
    # get dataset
    val_data_path = os.getcwd() + '/data/val'
    val_dataset = Local_dataset(val_data_path).get_dataset()
    val_dataset_batch = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)

    train_data_path = os.getcwd() + '/data/train'
    train_dataset = Local_dataset(train_data_path).get_dataset()
    train_dataset_batch = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # load model
    model = resnet34(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, 163)

    # set loss\optimizer\device
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learn_rate)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    writer = SummaryWriter(log_dir=log_dir)

    # for train
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for images, labels in train_dataset_batch:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            #print(loss.item())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch+1) % 10 == 0:
            torch.save(model, os.getcwd()+f'/model/model_full_epoch_{epoch+1}.pth')
        writer.add_scalar("Loss/train", total_loss, epoch+1)
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss:.4f}')
    
        # for eval
        if (epoch+1) % 10 == 0:
            model.eval()
            correct, total = 0, 0
            with torch.no_grad():
                for images, labels in val_dataset_batch:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    _, predicted = torch.max(outputs, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
            writer.add_scalar("Accuracy/train", 100 * correct / total, epoch+1)
            print(f'Accuarcy: {100 * correct / total:.2f}%')
    writer.close()

if __name__ == '__main__':
    main()