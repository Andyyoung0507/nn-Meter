# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import os

from ..interface import BaseBackend
from nn_meter.utils.path import get_filename_without_ext


class OpenVINOBackend(BaseBackend):
    parser_class = None
    runner_class = None

    def update_configs(self):
        """update the config parameters for OpenVINO platform
        """
        super().update_configs()
        self.runner_kwargs.update({
            'venv': self.configs['OPENVINO_ENV'],
            'optimizer': self.configs['OPTIMIZER_PATH'],
            'runtime_dir': self.configs['OPENVINO_RUNTIME_DIR'],
            'serial': self.configs['DEVICE_SERIAL'],
            'data_type': self.configs['DATA_TYPE'],
        })
        self.venv = self.configs['OPENVINO_ENV']
    
    def convert_model(self, model, model_name, savedpath, input_shape=None):
        """convert the Keras model instance to frozen pb file
        """
        from .utils.converters import keras_model_to_frozenpb
        from .frozenpb_patcher import patch_frozenpb
        model_tmp_dir = os.path.join(savedpath, model_name)
        pb_path, _ = keras_model_to_frozenpb(model, model_tmp_dir, model_name, input_shape)
        patched_pb_path = patch_frozenpb(pb_path, os.path.join(self.venv, 'bin/python'))
        return patched_pb_path

    def profile(self, model, model_name, savedpath, input_shape, metrics=['latency']):
        """convert the model to the backend platform and run the model on the backend, return required metrics 
        of the running results. We only support latency for metric by now.
        """
        patched_pb_path = self.convert_model(model, model_name, savedpath, input_shape)
        self.runner.load_graph(patched_pb_path, os.path.join(self.tmp_dir, model_name))
        return self.parser.parse(self.runner.run(input_shape)).results.get(metrics)
