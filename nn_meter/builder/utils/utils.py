# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import os
import json


def get_inputs_by_shapes(shapes):
    from tensorflow import keras
    if len(shapes) == 1:
        return keras.Input(shape=shapes[0], batch_size=1)
    else:
        return [keras.Input(shape=shape, batch_size=1) for shape in shapes]


def get_tensor_by_shapes(shapes):
    import tensorflow as tf
    if len(shapes) == 1:
        return tf.random.normal(shape = [1] + shapes[0])
    else:
        return [tf.random.normal(shape = [1] + shape) for shape in shapes]


def merge_prev_info(new_info, info_save_path = None, prev_info = None):
    ''' merge new_info with previous info and return the updated info. This method is used in two cases: 

    1. before save `new_info` to `info_save_path`, we need to check if the `info_save_path` is empty. If `info_save_path`
    is not empty, this method will help merge the previous info saved in `info_save_path` for a incrementally storage and
    avoid information loss. In this case, params `new_info` and `info_save_path` are needed.

    2. extend the dictionary of `prev_info` with `new_info`. In this case, params `new_info` and `prev_info` are needed.
    
    @params
    
    new_info (dict): new information
    
    info_save_path (str): the path to save the new info. We need to check if the path is empty and mantain the previous info
        in `info_save_path`.
    
    prev_info (dict): the previous information
    '''
    if (info_save_path == None and prev_info == None) or (info_save_path != None and prev_info != None):
        raise ValueError("One and only one params of `info_save_path` and `prev_info` is needed.")

    if info_save_path != None and os.path.isfile(info_save_path):
        with open(info_save_path, 'r') as fp:
            prev_info = json.load(fp)

    if prev_info == None:
        return new_info

    for module_key in new_info.keys():
        if module_key in prev_info:
            prev_info[module_key].update(new_info[module_key])
        else:
            prev_info[module_key] = new_info[module_key]
    return prev_info
