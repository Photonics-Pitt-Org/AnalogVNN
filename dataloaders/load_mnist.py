from typing import Type

from torch.utils.data import DataLoader
from torchvision.datasets import VisionDataset
from torchvision.transforms import transforms


def load_dataset(dataset: Type[VisionDataset], path, batch_size, is_cuda=False) -> (DataLoader, DataLoader, tuple):
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    dataset_kwargs = {
        'batch_size': batch_size,
        'shuffle': True
    }

    if not is_cuda:
        cuda_kwargs = {
            'num_workers': 1,
            'pin_memory': True,
        }
        dataset_kwargs.update(cuda_kwargs)

    train_set = dataset(root=path, train=True, download=True, transform=transform)
    train_loader = DataLoader(train_set, **dataset_kwargs)

    test_set = dataset(root=path, train=False, download=True, transform=transform)
    test_loader = DataLoader(test_set, **dataset_kwargs)

    input_shape = tuple([batch_size] + list(train_set.data.shape)[1:])

    return train_loader, test_loader, input_shape, tuple(dataset.classes)
