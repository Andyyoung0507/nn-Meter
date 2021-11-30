# Build the Rule Tester

A rule tester creates a series of models (what we call "test cases" in nn-Meter), runs the models on a given device, profiles the model to get its latency, and finally, detects the fusion rules for every pair of ops. To build a rule tester, there are four steps to implement the rule detection.

## Step 1. Prepare Backends and Create Workspace

The first step to run rule_tester is to prepare a backends. Users could follow guidance [here](./backend.md) to prepare workspace and create workspace.

After creating the workspace, a yaml file named `ruletest_config.yaml` will be placed in `<workspace-path>/configs/`. The ruletest configs includes:

TODO: @Jianyu
- `default_input_shape`: [28, 28, 16],
- `d1_input_shape`: [428],
- `filters`: 256,
- `kernel_size`: 3,
- `enabled`: ['BF', 'MON', 'RT'],
- `params`: {
    `BF`: {
        `eps`: 0.5,
        }
    },
- `model_dir`: '',
- `detail`: False,

Users could open `<workspace-path>/configs/ruletest_config.yaml` and edit the content. The config will take effect after the the config file is saved and closed.

The workspace folder should be declared before building the rule_tester:

```python
from nn_meter.builder.utils import builder_config

builder_config.init(
    platform_type="tflite", 
    workspace_path="path/to/workspace/folder"
) # change the text to required platform type and workspace path
```
## Step 2. Create testcases
According to `<workspace-path>/configs/ruletest_config.yaml`, the testcases can be created by running:

```python
from nn_meter.builder import create_testcases

# generate testcases
origin_testcases = create_testcases()
```

The test case models will be saved in `<workspace-path>/testcases/`, and the test case dictionary will be saved in `<workspace-path>/results/origin_testcases.json`.

## Step 3. Run Test Cases on Given Backend
Given required backend, users could run test cases model and get profiled latency value by running:

```python
from nn_meter.builder.backend import connect_backend
from nn_meter.builder import run_testcases

# initialize backend
backend = connect_backend(backend='tflite_cpu', workspace_path=workspace_path)

# run testcases and collect profiling results
profiled_testcases = run_testcases(backend, origin_testcases)
```
`backend` refers to the framework of the platform and device to execute the model. Currently we provide three instance on two platforms, i.e., CPU backend, GPU backend with TFLite platform, and VPU backend with OpenVINO platform. Refer to [backend guidance](./backend.md) for how to setup the device and get connection to the backend. To use the customized backend, users can follow the [customize backend guidance](./build_customized_backend.md).

The profiled test cases dictionary will be saved in `<workspace-path>/results/profiled_testcases.json`.

## Step 4. Detect Fusion Rule
```python
from nn_meter.builder import detect_fusionrule

# determine fusion rules from profiling results
detected_testcases = detect_fusionrule(profiled_testcases)
```

Two ops will be considered as fused if ... #TODO

## Data Structure of TestCases
Each test case consists of several test models to profile, indicating two ops and a block combining the two ops, respectively. In each part, `"model"` points to its directory to the path of this ops' Keras model, `"shapes"` indicates the input shape of the tensor to test, and `"latency"` reports the profiled results after running `run_testcases`. This is a json dump of generated testcases. Note that the `"latency"` attribute appears after the testcases running.

```json
{
    "BF_dwconv_relu": {
        "dwconv": {
            "model": "./test_models/BF_dwconv_relu_dwconv",
            "shapes": [
                [
                    28,
                    28,
                    16
                ]
            ],
            "latency": "41.781 +- 1.0"
        },
        "relu": {
            "model": "./test_models/BF_dwconv_relu_relu",
            "shapes": [
                [
                    28,
                    28,
                    16
                ]
            ],
            "latency": "2.36618 +- 0.0"
        },
        "block": {
            "model": "./test_models/BF_dwconv_relu_block",
            "shapes": [
                [
                    28,
                    28,
                    16
                ]
            ],
            "latency": "41.4198 +- 1.0"
        }
    },
    ...
}
```
In this instance, `BF_dwconv_relu` is the name of a rule. Here, there are three models called `dwconv`, `relu` and `block`. For each model, the `model` field is the path to where the model is saved. `shapes` is its inputs. For example, here `[[28, 28, 16]]` means this model has only one input, and the shape is `(28, 28, 16)`.

## End-to-end Demo
Here is an end-to-end demo for the progress of the rule tester:
```python
from nn_meter.builder.utils import builder_config
from nn_meter.builder.backends import connect_backend
from nn_meter.builder import create_testcases, run_testcases, detect_fusionrule

# create workspace folder
builder_config.init(
    platform_type="tflite", 
    workspace_path="path/to/workspace/folder"
)

# initialize backend
backend = connect_backend(backend='tflite_cpu', workspace_path=workspace_path)

# generate testcases
origin_testcases = create_testcases()

# run testcases and collect profiling results
profiled_testcases = run_testcases(backend, origin_testcases)

# determine fusion rules from profiling results
detected_testcases = detect_fusionrule(profiled_testcases)
```

After each step, the output will be dumped to `<workspace-path>/results/`. Both the testcases instance and path string to the dumped testcases file are acceptable for the next step.

Also note that it's optional to use a backend. What `run_testcases` do is just collecting latency results of each testcases, so you can use your own tools to measure the latency. Refer to implementation of `run_testcases` for how to fill back the latency.