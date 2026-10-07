import torch
from torch import nn

class NormalizedModel(nn.Module):
    """Keep attacks and perturbation metrics in [0, 1] image coordinates."""
    def __init__(self, model, normalization=None):
        super().__init__()
        self.model = model
        if normalization is None:
            mean, std = (0, 0, 0), (1, 1, 1)
        else:
            mean, std = normalization
        self.register_buffer('mean', torch.tensor(mean).float().view(1, 3, 1, 1))
        self.register_buffer('std', torch.tensor(std).float().view(1, 3, 1, 1))

    def forward(self, images):
        return self.model((images - self.mean) / self.std)
