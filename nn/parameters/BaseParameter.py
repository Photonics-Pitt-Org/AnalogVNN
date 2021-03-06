import torch
from torch import nn
from torch.nn import Parameter


class BaseParameter(Parameter):
    def __new__(cls, data=None, requires_grad=True, *args, **kwargs):
        if data is None:
            data = torch.tensor([])
        # noinspection PyTypeChecker
        return torch.Tensor._make_subclass(cls, data, requires_grad)

    # noinspection PyUnusedLocal
    def __init__(self, data=None, requires_grad=True):
        super(BaseParameter, self).__init__()

    def __repr__(self):
        return super(BaseParameter, self).__repr__()

    @classmethod
    def from_tensor(cls, tensor, *args, **kwargs):
        return cls(data=tensor, requires_grad=tensor.requires_grad, *args, **kwargs)

    @classmethod
    def from_parameter(cls, parameter, *args, **kwargs):
        return cls(data=parameter, requires_grad=parameter.requires_grad, *args, **kwargs)

    @classmethod
    def convert_model(cls, model: nn.Module, *args, **kwargs):
        with torch.no_grad():
            for name, parameter in model.named_parameters(recurse=False):
                if isinstance(parameter, cls):
                    continue

                if not parameter.requires_grad:
                    continue

                setattr(
                    model,
                    name,
                    cls.from_parameter(parameter=parameter, *args, **kwargs)
                )

            for module in model.modules():
                if module == model:
                    continue
                cls.convert_model(module, *args, **kwargs)
