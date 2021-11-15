import json
import os
from pathlib import Path
from typing import List, Dict, Union

import matplotlib
import seaborn as seaborn
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from tensorboard.plugins.hparams.metadata import SESSION_START_INFO_TAG
from tensorboard.plugins.hparams.plugin_data_pb2 import HParamsPluginData
from tensorflow.python.summary.summary_iterator import summary_iterator


def collect_parameters_to_json(path):
    tensorboard_dir = Path(path).joinpath("tensorboard")
    all_files: List[Path] = []
    for root, dirs, files in os.walk(tensorboard_dir):
        for file in files:
            all_files.append(Path(root).joinpath(file))
    parameter_data = {}
    # c = False
    for i, file in enumerate(all_files):
        name = file.parent
        if "_" not in str(name.name):
            name = name.parent
            # c = True
        name = name.name
        print(f"[{i}/{len(all_files)}] Processing {name}...")
        if name not in parameter_data:
            parameter_data[name] = {
                "test_accuracy": {},
                "train_accuracy": {},
                "test_loss": {},
                "train_loss": {},
                "parameters": {},
                # "raw": [],
            }

        this_data = parameter_data[name]
        for event in summary_iterator(str(file)):
            for value in event.summary.value:
                if value.tag == 'Accuracy/test':
                    this_data["test_accuracy"][int(event.step)] = value.simple_value
                    continue
                if value.tag == 'Loss/test':
                    this_data["train_accuracy"][int(event.step)] = value.simple_value
                    continue
                if value.tag == 'Accuracy/train':
                    this_data["test_loss"][int(event.step)] = value.simple_value
                    continue
                if value.tag == 'Loss/train':
                    this_data["train_loss"][int(event.step)] = value.simple_value
                    continue
                if value.tag == SESSION_START_INFO_TAG:
                    ssi = HParamsPluginData()
                    ssi.ParseFromString(value.metadata.plugin_data.content)
                    hparams = dict(ssi.session_start_info.hparams)
                    for k in hparams:
                        hparams[k] = hparams[k].ListFields()[0][1]
                    this_data["parameters"] = hparams
            # this_data["raw"].append(event)

        # if c:
        # break
    file_path = tensorboard_dir.parent.joinpath(f"{Path(path).name.split('.')[0]}_full_parameter_data.json")
    with open(file_path, "w") as file:
        file.write(json.dumps(parameter_data))

    return file_path


def create_figure(json_file_path):
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    json_file_path = Path(json_file_path)
    with open(json_file_path, "r") as file:
        run_data: Dict[str, Dict[str, Union[float, str, Dict[str, Union[str, float]]]]] = json.loads(file.read())

    max_accuracies: Dict[str, float] = {}
    parameters_map: Dict[str, Dict[str, Union[str, float]]] = {}
    for key, value in run_data.items():
        key = key[key.find("_") + 1:]
        if key in max_accuracies:
            max_accuracies[key] = max(*value["test_accuracy"].values(), max_accuracies[key])
        else:
            max_accuracies[key] = max(value["test_accuracy"].values())
            parameters_map[key] = value["parameters"]

    x = []
    y = []
    hue = []
    for key, value in max_accuracies.items():
        x.append(parameters_map[key]["norm_class_w"])
        hue.append(parameters_map[key]['norm_class_y'])
        y.append(value)

    fig = figure()
    fig.set_size_inches(8, 5)
    fig.set_dpi(200)
    seaborn.violinplot(x=x, y=y, hue=hue, cut=0, palette="Set2", inner=None, linewidth=0.5)
    fig.tight_layout()
    plt.show()
    fig.savefig('image.svg', dpi=fig.dpi)
    print()


if __name__ == '__main__':
    # json_file = collect_parameters_to_json("C:/_data/tensorboard_cleo_run_1_D.py")
    create_figure("C:/_data/tensorboard_cleo_run_1_D.py/tensorboard_cleo_run_1_D_full_parameter_data.json")
    print()