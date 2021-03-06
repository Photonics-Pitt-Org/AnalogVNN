import torch
from torch import nn, Tensor

from nn.BaseLayer import BaseLayer
from nn.backward_pass.BackwardFunction import BackwardIdentity


def reduce_precision(x: Tensor, precision: int, divide: float):
    g: Tensor = x * precision
    f = torch.sign(g) * torch.maximum(
        torch.floor(torch.abs(g)),
        torch.ceil(torch.abs(g) - divide)
    ) * (1 / precision)
    return f


class ReducePrecision(BaseLayer, BackwardIdentity):
    __constants__ = ['precision', 'divide']
    precision: nn.Parameter
    divide: nn.Parameter

    def __init__(self, precision: int = 8, divide: float = 0.5):
        super(ReducePrecision, self).__init__()
        if precision < 1:
            raise ValueError(f"precision has to be more than 0, but got {precision}")

        if precision != int(precision):
            raise ValueError(f"precision must be int, but got {precision}")

        if not (0 <= divide <= 1):
            raise ValueError(f"divide must be between 0 and 1, but got {divide}")

        self.precision = nn.Parameter(torch.tensor(precision), requires_grad=False)
        self.divide = nn.Parameter(torch.tensor(divide), requires_grad=False)

    @property
    def step_size(self) -> float:
        return 1 / self.precision

    def extra_repr(self) -> str:
        return f'precision={self.precision}, divide={self.divide}'

    def forward(self, x: Tensor):
        return reduce_precision(x, self.precision, self.divide)
