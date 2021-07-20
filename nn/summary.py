from collections import OrderedDict

import numpy as np
import torch
import torch.nn as nn


def summary(model: nn.Module, input_size=None):
    result = ""

    if input_size is None:
        input_size = tuple([1] + list(model.in_features[1:]))
        batch_size = model.in_features[0]
    else:
        batch_size = input_size[0]
        input_size = tuple(input_size[1:])

    device = next(model.parameters()).device

    def register_hook(module):

        def hook(module, input, output):
            class_name = str(module.__class__).split(".")[-1].split("'")[0]

            m_key = f"{class_name}-{len(summary) + 1:d}"
            summary[m_key] = OrderedDict()
            summary[m_key]["input_shape"] = list(input[0].size())
            summary[m_key]["input_shape"][0] = batch_size
            if isinstance(output, (list, tuple)):
                summary[m_key]["output_shape"] = [
                    [-1] + list(o.size())[1:] for o in output
                ]
            else:
                summary[m_key]["output_shape"] = list(output.size())
                summary[m_key]["output_shape"][0] = batch_size

            params = 0
            if hasattr(module, "weight") and hasattr(module.weight, "size"):
                params += torch.prod(torch.LongTensor(list(module.weight.size())))
                summary[m_key]["trainable"] = module.weight.requires_grad
            if hasattr(module, "bias") and hasattr(module.bias, "size"):
                params += torch.prod(torch.LongTensor(list(module.bias.size())))
            summary[m_key]["nb_params"] = params

        if (
                not isinstance(module, nn.Sequential)
                and not isinstance(module, nn.ModuleList)
                and not (module == model)
        ):
            hooks.append(module.register_forward_hook(hook))

    # multiple inputs to the network
    if isinstance(input_size, tuple):
        input_size = [input_size]

    # batch_size of 2 for batchnorm
    x = [torch.rand(2, *in_size).to(device) for in_size in input_size]

    # create properties
    summary = OrderedDict()
    hooks = []

    # register hook
    model.apply(register_hook)

    # make a forward pass
    model(*x)

    # remove these hooks
    for h in hooks:
        h.remove()

    rows = [["Layer (type)", "Output Shape", "Param #"]]
    total_params = 0
    total_output = 0
    trainable_params = 0
    for layer in summary:
        rows.append([
            layer,
            str(summary[layer]["output_shape"]),
            f"{summary[layer]['nb_params']:,}"
        ])

        total_params += summary[layer]["nb_params"]
        total_output += np.prod(summary[layer]["output_shape"])
        if "trainable" in summary[layer]:
            if summary[layer]["trainable"] == True:
                trainable_params += summary[layer]["nb_params"]

    # assume 4 bytes/number (float on cuda).
    total_input_size = abs(np.prod(input_size) * batch_size * 4. / (1024 ** 2.))
    total_output_size = abs(2. * total_output * 4. / (1024 ** 2.))  # x2 for gradients
    total_params_size = abs(total_params.numpy() * 4. / (1024 ** 2.))
    total_size = total_params_size + total_output_size + total_input_size

    col_size = [0] * len(rows[0])
    for row in rows:
        for i, v in enumerate(row):
            col_size[i] = max(len(v) + 4, col_size[i])

    line_size = np.sum(col_size)
    result += ("-" * line_size) + "\n"
    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            result += ("{:>" + str(col_size[j]) + "}").format(col)
        result += "\n"
        if i == 0:
            result += ("=" * line_size) + "\n"

    result += ("=" * line_size) + "\n"
    result += f"Total params: {total_params:,}\n"
    result += f"Trainable params: {trainable_params:,}\n"
    result += f"Non-trainable params: {total_params - trainable_params:,}\n"
    result += ("-" * line_size) + "\n"
    result += f"Input size (MB): {total_input_size:0.2f}\n"
    result += f"Forward/backward pass size (MB): {total_output_size:0.2f}\n"
    result += f"Params size (MB): {total_params_size:0.2f}\n"
    result += f"Estimated Total Size (MB): {total_size:0.2f}\n"
    result += ("-" * line_size) + "\n"
    return result
