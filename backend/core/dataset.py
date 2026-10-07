"""Load real images in pixel space; normalization belongs inside the model."""
from pathlib import Path
import torch
import torchvision
from torchvision import transforms
from torch.utils.data import DataLoader, Subset
from core.settings import DATA_DIR

NORMALIZATIONS = {
    'none': None,
    'cifar10': ((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    'imagenet': ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
}

def _loader(dataset, batch_size, num_samples, seed):
    if len(dataset) == 0:
        raise ValueError('数据集中没有可评测的图像')
    if num_samples is not None and num_samples < len(dataset):
        indices = torch.randperm(len(dataset), generator=torch.Generator().manual_seed(seed))[:num_samples]
        dataset = Subset(dataset, indices.tolist())
    return DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)

def get_cifar10_dataloader(train=False, batch_size=32, num_samples=None,
                           download=True, img_size=32, seed=42):
    transform = transforms.Compose([transforms.Resize((img_size, img_size)), transforms.ToTensor()])
    try:
        dataset = torchvision.datasets.CIFAR10(root=str(DATA_DIR), train=train,
                                              download=download, transform=transform)
    except Exception as error:
        raise ValueError('CIFAR-10 加载失败，请检查下载连接或本地数据；不会使用随机数据代替') from error
    return _loader(dataset, batch_size, num_samples, seed)

def get_custom_dataloader(dataset_path, batch_size=32, num_samples=None, img_size=224, seed=42):
    transform = transforms.Compose([transforms.Resize((img_size, img_size)), transforms.ToTensor()])
    dataset = torchvision.datasets.ImageFolder(root=str(Path(dataset_path)), transform=transform)
    return _loader(dataset, batch_size, num_samples, seed)
