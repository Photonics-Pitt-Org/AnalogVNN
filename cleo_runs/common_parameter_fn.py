from nn.layers.GaussianNoise import GaussianNoise
from nn.parameters.BasePrecisionParameter import BasePrecisionParameter


def normalize_parameter(norm_class):
    norm_object = norm_class()

    def set_parameter(parameter):
        if isinstance(parameter, BasePrecisionParameter):
            parameter.set_tensor(norm_object(parameter.pseudo_tensor))
        else:
            parameter.data = norm_object(parameter.data)

    return set_parameter


def add_gaussian_noise(leakage, precision):
    gaussian = GaussianNoise(leakage=leakage, precision=precision)

    def set_parameter(parameter):
        if isinstance(parameter, BasePrecisionParameter):
            parameter.set_tensor(gaussian(parameter.pseudo_tensor))
        else:
            parameter.data = gaussian(parameter.data)

    return set_parameter
