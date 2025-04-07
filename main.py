from source.load_dataset import Local_dataset
import os
from torch.utils.data import DataLoader
import visdom

batch_size = 32

def view_img(img):
    vis = visdom.Visdom()
    vis.images(img, win="batch_imgs", opts=dict(title='Random Image'))

def main():
    # get dataset
    data_path = os.getcwd() + '/data/val'
    dataset = Local_dataset(data_path).get_dataset()
    dataset_batch = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    for img, label in dataset_batch:
        view_img(img)
        break


if __name__ == '__main__':
    main()