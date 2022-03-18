# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import torch
import torch.nn as nn
from .utils import get_padding, get_output_shape_with_padding
from ..interface import BaseOperator

'''
This file contains the torch implementation of operators
'''

#---------------------- convolution layer ----------------------#

class Conv(BaseOperator):
    def get_model(self):
        cin = self.input_shape[0]
        cout = cin if "COUT" not in self.config else self.config["COUT"]
        padding = get_padding(self.config["KERNEL_SIZE"], self.config["STRIDES"], self.input_shape[1])
        return nn.Conv2d(cin, cout, kernel_size=self.config["KERNEL_SIZE"], stride=self.config["STRIDES"], padding=padding)

    def get_output_shape(self):
        cout = self.input_shape[0] if "COUT" not in self.config else self.config["COUT"]
        output_h = (self.input_shape[1] - 1) // self.config["STRIDES"] + 1
        output_w = (self.input_shape[2] - 1) // self.config["STRIDES"] + 1
        return [cout, output_h, output_w]


class DwConv(BaseOperator):
    def get_model(self):
        cin = self.input_shape[0]
        padding = get_padding(self.config["KERNEL_SIZE"], self.config["STRIDES"], self.input_shape[1])
        return nn.Conv2d(cin, cin, kernel_size=self.config["KERNEL_SIZE"], stride=self.config["STRIDES"], padding=padding, groups=cin)

    def get_output_shape(self):
        cin = self.input_shape[0]
        output_h = (self.input_shape[1] - 1) // self.config["STRIDES"] + 1
        output_w = (self.input_shape[2] - 1) // self.config["STRIDES"] + 1
        return [cin, output_h, output_w]


class ConvTrans(BaseOperator):
    def get_model(self):
        raise NotImplementedError
        cin = self.input_shape[0]
        cout = cin if "COUT" not in self.config else self.config["COUT"]
        return nn.ConvTranspose2d(cin, cout, kernel_size=self.config["KERNEL_SIZE"], stride=self.config["STRIDES"], padding=1)

    def get_output_shape(self):
        cout = self.input_shape[0] if "COUT" not in self.config else self.config["COUT"]
        return [cout, self.input_shape[1] * self.config["STRIDES"], self.input_shape[2] * self.config["STRIDES"]]

#------------------ normalization and pooling ------------------#

class BN(BaseOperator):
    def get_model(self):
        cin = self.input_shape[0]
        return nn.BatchNorm2d(cin)


class GlobalAvgpool(BaseOperator):
    def get_model(self):
        raise NotImplementedError


class MaxPool(BaseOperator):
    def get_model(self):
        if "POOL_STRIDES" not in self.config:
            self.config["POOL_STRIDES"] = self.config["STRIDES"]
        padding = get_padding(self.config["KERNEL_SIZE"], self.config["POOL_STRIDES"], self.input_shape[1])
        return nn.MaxPool2d(self.config["KERNEL_SIZE"], self.config["POOL_STRIDES"], padding=padding)

    def get_output_shape(self):
        cin = self.input_shape[0]
        if "POOL_STRIDES" not in self.config:
            self.config["POOL_STRIDES"] = self.config["STRIDES"]
        output_h = (self.input_shape[1] - 1) // self.config["POOL_STRIDES"] + 1
        output_w = (self.input_shape[2] - 1) // self.config["POOL_STRIDES"] + 1
        return [cin, output_h, output_w]


class AvgPool(BaseOperator):
    def get_model(self):
        if "POOL_STRIDES" not in self.config:
            self.config["POOL_STRIDES"] = self.config["STRIDES"]
        padding = get_padding(self.config["KERNEL_SIZE"], self.config["POOL_STRIDES"], self.input_shape[1])
        return nn.AvgPool2d(self.config["KERNEL_SIZE"], self.config["POOL_STRIDES"], padding=padding)

    def get_output_shape(self):
        cin = self.input_shape[0]
        if "POOL_STRIDES" not in self.config:
            self.config["POOL_STRIDES"] = self.config["STRIDES"]
        output_h = (self.input_shape[1] - 1) // self.config["POOL_STRIDES"] + 1
        output_w = (self.input_shape[2] - 1) // self.config["POOL_STRIDES"] + 1
        return [cin, output_h, output_w]

#------------------------ other modules ------------------------#

class SE(BaseOperator):
    def get_model(self):
        raise NotImplementedError


class FC(BaseOperator):
    def get_model(self):
        cin = self.input_shape[0]
        cout = self.input_shape[0] if "COUT" not in self.config else self.config["COUT"]
        return nn.Linear(cin, cout)

    def get_output_shape(self):
        cout = self.input_shape[0] if "COUT" not in self.config else self.config["COUT"]
        return [cout] + self.input_shape[1:]

#-------------------- activation function --------------------#

class Relu(BaseOperator):
    def get_model(self):
        return nn.ReLU()


class Relu6(BaseOperator):
    def get_model(self):
        return nn.ReLU()


class Sigmoid(BaseOperator):
    def get_model(self):
        return nn.Sigmoid()


class Hswish(BaseOperator):
    def get_model(self):
        return nn.Hardswish()

#---------------------- basic operation ----------------------#

class Reshape(BaseOperator):
    def get_model(self):
        raise NotImplementedError


class Add(BaseOperator):
    def get_model(self):
        raise NotImplementedError


class Concat(BaseOperator):
    def get_model(self):
        raise NotImplementedError


class Flatten(BaseOperator):
    def get_model(self):
        raise NotImplementedError


class Split(BaseOperator):
    def get_model(self):
        cin = self.input_shape[0]
        def func(inputs):
            return torch.split(inputs, [cin // 2, cin - cin // 2], dim=0)
        return func

    def get_output_shape(self):
        return [self.input_shape[0] // 2, self.input_shape[1], self.input_shape[2]]
