# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import os
from tensorflow import keras

from silence_tensorflow import silence_tensorflow
silence_tensorflow()

def get_output_folder(parent_dir, run_name):
    """
    Return save folder.

    Assumes folders in the parent_dir have suffix -run{run
    number}. Finds the highest run number and sets the output folder
    to that number + 1. This is just convenient so that if you run the
    same script multiple times tensorboard can plot all of the results
    on the same plots with different names.

    Parameters
    ----------
    parent_dir: str
      Path of the directory containing all experiment runs.
    run_name: str
      Name of the run

    Returns
    -------
    parent_dir/run_dir
      Path to this run's save directory.
    """
    os.makedirs(parent_dir, exist_ok = True)
    experiment_id = 0
    for folder_name in os.listdir(parent_dir):
        if not os.path.isdir(os.path.join(parent_dir, folder_name)):
            continue
        try:
            folder_name = int(folder_name.split('-run')[-1])
            if folder_name > experiment_id:
                experiment_id = folder_name
        except:
            pass
    experiment_id += 1

    parent_dir = os.path.join(parent_dir, run_name)
    parent_dir = parent_dir + '-run{}'.format(experiment_id)
    os.makedirs(parent_dir, exist_ok = True)
    return parent_dir


def get_op_is_two_inputs(op_name):
    if op_name in ["conv", "dwconv", "convtrans", "pooling", "se", "dense", "relu", "hswish", "reshape"]:
        return False
    elif op_name in ["add", "concat"]:
        return True
    else:
        raise ValueError(f"Unsupported operator name: {op_name} in rule-tester.")


def save_testcase(testcase):
    model_path = os.path.join(self.model_dir, self.name + '_' + op)
    model['model'](get_tensor_by_shapes(model['shapes']))
    keras.models.save_model(model['model'], model_path)
    testcase[op]['model'] = model_path