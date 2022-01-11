# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
from nn_meter.utils.registry import Registry
from nn_meter.utils.path import get_filename_without_ext

BACKENDS = Registry('backends')

class BaseBackend:
    """
    the base backend class to instantiate a backend instance. If users want to implement their own backend,
    the customized Backend should inherit this class.

    @params:

    runner_class: a subclass inherit form `nn_meter.builder.backend.BaseRunner` to specify the running command of
        the backend. A runner contains commands to push the model to mobile device, run the model on the mobile device,
        get stdout from the mobile device, and related operations. In the implementation of a runner, an interface of
        ``Runner.run()`` is required.
    
    parser_class: a subclass inherit form `nn_meter.builder.backend.BaseParser` to parse the profiled results.
        A parser parses the stdout from runner and get required metrics. In the implementation of a parser, interface
        of `Parser.parse()` and property of `Parser.results()` are required.
    """
    runner_class = None
    parser_class = None

    def __init__(self, configs):
        """ class initialization with required configs
        """
        self.configs = configs
        self.update_configs()
        self.parser = self.parser_class(**self.parser_kwargs)
        self.runner = self.runner_class(**self.runner_kwargs)

    def update_configs(self):
        """ update the config parameters for the backend
        """
        self.parser_kwargs = {}
        self.runner_kwargs = {}
    
    def convert_model(self, model, model_name, savedpath, input_shape=None):
        """ convert the Keras model instance to the type required by the backend inference
        """
        return model

    def profile(self, model, model_name, savedpath, input_shape=None, metrics=['latency']):
        """
        convert the model to the backend platform and run the model on the backend, return required metrics 
        of the running results. nn-Meter only support latency for metric by now. Users may provide other
        metrics in their customized backend.

        @params:
        
        model: the Keras model waiting to profile
        
        model_name: the name of the model
        
        savedpath: path to save the converted model
        
        input_shape: the shape of input tensor for inference, a random tensor according to the shape will be 
            generated and used
        
        metrics: a list of required metrics name. Defaults to ['latency']
        
        """
        converted_model = self.convert_model(model, model_name, savedpath, input_shape)
        return self.parser.parse(self.runner.run(converted_model)).results.get(metrics)

    def profile_model_file(self, model_path, savedpath, input_shape = None, metrics = ['latency']):
        """ load model by model file path and run ``self.profile()``
        """
        import tensorflow as tf
        model_name = get_filename_without_ext(model_path)
        model = tf.keras.models.load_model(model_path)
        return self.profile(model, model_name, savedpath, input_shape, metrics)

    def test_connection(self):
        """ check the status of backend interface connection.
        """
        pass


class BaseRunner:
    """
    Specify the running command of the backend. A runner contains commands to push the model to mobile device, run the model 
    on the mobile device, get stdout from the mobile device, and related operations. 
    """
    def run(self):
        """ Main steps of ``Runner.run()`` includes 1) push the model file to edge devices, 2) run models in required times
        and get back running results. Return the running results on edge device.
        """
        output = ''
        return output


class BaseParser:
    """
    Parse the profiled results. A parser parses the stdout from runner and get required metrics.
    """
    def parse(self, content):
        """ A string parser to parse profiled results value from the standard output of devices runner. This method should return the instance
        class itself.

        @params
        
        content: the standard output from device runner       
        """
        return self

    @property
    def results(self):
        """ warp the parsed results by ``ProfiledResults`` class from ``nn_meter.builder.backend_meta.utils`` and return the parsed results value.
        """
        pass


def connect_backend(backend_name):
    """ 
    Return the required backend class, and feed params to the backend. Supporting backend: tflite_cpu, tflite_gpu, openvino_vpu.
    
    Available backend and corresponding configs: 
    - For backend based on TFLite platform: {
        'MODEL_DIR': path to the folder (on host device) where temporary models will be generated.
        'REMOTE_MODEL_DIR': path to the folder (on mobile device) where temporary models will be copied to.
        'KERNEL_PATH': path (on mobile device) where the kernel implementations will be dumped.
        'BENCHMARK_MODEL_PATH': path (on android device) where the binary file `benchmark_model` is deployed.
        'DEVICE_SERIAL': if there are multiple adb devices connected to your host, you need to provide the \\
                         corresponding serial id. Set to '' if there is only one device connected to your host.
    }
    - For backend based on OpenVINO platform: {
        'OPENVINO_ENV': path to openvino virtualenv (./docs/requirements/openvino_requirements.txt is provided)
        'OPTIMIZER_PATH': path to openvino optimizer
        'OPENVINO_RUNTIME_DIR': directory to openvino runtime
        'DEVICE_SERIAL': serial id of the device
        'DATA_TYPE': data type of the model (e.g., fp16, fp32)
    }
    
    The config can be declared and modified after create a workspace. Users could follow guidance from ./docs/builder/backend.md
    
    @params:
    backend: name of backend or backend class (subclass instance of `BaseBackend`). 
    """
    if isinstance(backend_name, str):
        backend_cls = BACKENDS.get(backend_name)
    else:
        backend_cls = backend_name

    # load configs from workspace
    from nn_meter.builder import builder_config
    configs = builder_config.get_module('backend')
    return backend_cls(configs)

def list_backends():      
    return BACKENDS.items()
