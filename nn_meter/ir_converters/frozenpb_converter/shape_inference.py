# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
from .protobuf_helper import ProtobufHelper as ph
from functools import reduce
import copy
import math
import logging


logging = logging.getLogger(__name__)


class ShapeInference:
    @staticmethod
    def eval_prodcast(graphe, node):
        """
        Evalute the prodcast along the input nodes.
        Now we use lazy prodcast, will move to tf implement later.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        input_nodes = node["inbounds"]
        if len(input_nodes) < 2:
            logging.warn(
                "Invalid input op num for prodcast op %s" % (node["attr"]["name"])
            )
            if len(input_nodes) == 1:
                return graphe[node["inbounds"][0]]["attr"]["output_shape"][0]
            else:
                return None

        target_dim = -1
        target_shape = [1]
        input_shape_list = []
        for node_name in input_nodes:
            input_shape = graphe[node_name]["attr"]["output_shape"][0]
            input_shape_list.append(input_shape)
            if target_dim < len(input_shape):
                target_dim = len(input_shape)
                target_shape = input_shape
            elif target_dim == len(input_shape):
                for i in range(target_dim):
                    if target_shape[i] < input_shape[i]:
                        target_shape[i] = input_shape[i]

        return input_shape_list, [target_shape]

    @staticmethod
    def get_padding_shape(input_shape, cout, k_size, strides, padding):
        """
        Calculate the padded shape of a given tensor.

        Parameters
        ----------
        input_shape : list
            Input shape in list, a 2D or 4D list.
        cout : int
            Cout of the operation.
        k_size : list
            Kernel size of the operation, a 2D or 4D list.
        strides : list
            Strides of the operation, a 2D or 4D list.
        padding : str
            Padding type, now support SAME and VALID.
        """

        logging.debug(
            "Calculating padding shape, input shape: %s, kernel size: %s, strides: %s, padding: %s."
            % (str(input_shape), str(k_size), str(strides), str(padding))
        )

        if padding == "SAME":
            outh = math.ceil(ph.get_h(input_shape) / ph.get_h(strides))
            outw = math.ceil(ph.get_w(input_shape) / ph.get_w(strides))

            padh = max(
                (outh - 1) * ph.get_h(strides)
                + ph.get_h(k_size)
                - ph.get_h(input_shape),
                0,
            )
            padw = max(
                (outw - 1) * ph.get_w(strides)
                + ph.get_w(k_size)
                - ph.get_w(input_shape),
                0,
            )

            pad_top = padh // 2
            pad_bottom = padh - pad_top
            pad_left = padw // 2
            pad_right = padw - pad_left

            pad_size = [pad_top, pad_bottom, pad_left, pad_right]
        elif padding == "VALID":
            outh = math.ceil(
                (ph.get_h(input_shape) - ph.get_h(k_size) + 1) / ph.get_h(strides)
            )
            outw = math.ceil(
                (ph.get_h(input_shape) - ph.get_h(k_size) + 1) / ph.get_w(strides)
            )

            pad_size = [0, 0, 0, 0]
        else:
            logging.error("Unexpected padding format %s." % (padding))
            return None, None

        output_shape = list(map(int, [input_shape[0], outh, outw, cout]))
        return copy.deepcopy(output_shape), copy.deepcopy(pad_size)

    @staticmethod
    def Const_get_shape(graphe, node):
        """
        Get shape of a const operator.
        Take the tensor shape as the output shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return [], [node["attr"]["attr"]["tensor_shape"]]

    @staticmethod
    def Identity_get_shape(graphe, node):
        """
        Get shape of an Identity operator.
        This is not well implemented, will move a more robust later.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return [], [graphe[node["inbounds"][0]]["attr"]["output_shape"][0]]

    @staticmethod
    def propogate_shape(graphe, node):
        """
        For operator who does not affact the shapes.
        Just take the input shapes as output.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        logging.debug("Propogate through op %s.", node["attr"]["name"])
        in_shape = [graphe[node["inbounds"][0]]["attr"]["output_shape"][0]]
        return in_shape, in_shape

    @staticmethod
    def FusedBatchNorm_get_shape(graphe, node):
        """
        Get shape of a FusedBatchNorm operator.
        Just propogate the shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.propogate_shape(graphe, node)

    @staticmethod
    def BiasAdd_get_shape(graphe, node):
        """
        Get shape of a BiasAdd operator.
        Just propogate the shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.propogate_shape(graphe, node)

    @staticmethod
    def Relu_get_shape(graphe, node):
        """
        Get shape of a Relu operator.
        Just propogate the shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.propogate_shape(graphe, node)

    @staticmethod
    def Relu6_get_shape(graphe, node):
        """
        Get shape of a Relu6 operator.
        Just propogate the shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.propogate_shape(graphe, node)

    @staticmethod
    def LeakyReLU_get_shape(graphe, node):
        """
        Get shape of a LeakyReLU operator.
        Just propogate the shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.propogate_shape(graphe, node)

    @staticmethod
    def Add_get_shape(graphe, node):
        """
        Get shape of an Add operator.
        Just propogate the shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.eval_prodcast(graphe, node)

    @staticmethod
    def Mul_get_shape(graphe, node):
        """
        Get shape of an FusedBatchNorm operator.
        Just propogate the shape.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.eval_prodcast(graphe, node)

    @staticmethod
    def Pool_get_shape(graphe, node):
        """
        Get shape of a Pooling type operation.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        if len(node["inbounds"]) != 1:
            logging.warning("Failed to get input node of %s." % (node["attr"]["name"]))
            logging.debug(node)
            return

        input_shape = copy.deepcopy(
            graphe[node["inbounds"][0]]["attr"]["output_shape"][0]
        )
        logging.debug(
            "Get input shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], node["inbounds"][0], input_shape)
        )

        k_size = node["attr"]["attr"]["ksize"]

        if node["attr"]["attr"]["strides"][::3] != [1, 1]:
            logging.warning(
                "Invalid strides %s of node %s."
                % (str(node["attr"]["attr"]["strides"]), node["attr"]["name"])
            )
            logging.debug(node)
            return

        strides = node["attr"]["attr"]["strides"]
        padding = node["attr"]["attr"]["padding"].decode("utf-8")
        logging.debug(
            "Op:%s, stride:%s, padding:%s."
            % (node["attr"]["name"], str(strides), str(padding))
        )

        out_shape, padding_shape = ShapeInference.get_padding_shape(
            input_shape, input_shape[3], k_size, strides, padding
        )

        node["attr"]["attr"]["ksize"] = copy.deepcopy(
            node["attr"]["attr"]["ksize"][1:-1]
        )
        node["attr"]["attr"]["strides"] = copy.deepcopy(
            node["attr"]["attr"]["strides"][1:-1]
        )
        node["attr"]["attr"]["pads"] = copy.deepcopy(padding_shape)

        return [input_shape], [out_shape]

    @staticmethod
    def AvgPool_get_shape(graphe, node):
        """
        Get shape of an AvgPool operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Pool_get_shape(graphe, node)

    @staticmethod
    def AveragePooling2D_get_shape(graphe, node):
        """
        Get shape of an AveragePooling2D operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Pool_get_shape(graphe, node)

    @staticmethod
    def MaxPool_get_shape(graphe, node):
        """
        Get shape of a MaxPool operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Pool_get_shape(graphe, node)

    @staticmethod
    def MaxPooling2D_get_shape(graphe, node):
        """
        Get shape of a MaxPooling2D operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Pool_get_shape(graphe, node)

    @staticmethod
    def Placeholder_get_shape(graphe, node):
        """
        Get shape of a Placeholder operator.
        This fetch the shape from the shape attibute of the operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return [], [node["attr"]["attr"]["shape"]]

    @staticmethod
    def Conv2D_get_shape(graphe, node):
        """
        Get shape of a Conv2D operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        weight_node = ph.find_weights_root(graphe, node)
        if len(weight_node) != 1:
            logging.warning("Failed to get shape of node %s." % (node["attr"]["name"]))
            logging.debug(node)
            return

        input_node = [x for x in node["inbounds"] if x != weight_node]
        input_node = [x for x in input_node if graphe[x]["attr"]["type"] != "Identity"]
        if len(input_node) != 1:
            logging.warning("Failed to get input node of %s." % (node["attr"]["name"]))
            logging.debug(node)
            return

        input_shape = copy.deepcopy(graphe[input_node[0]]["attr"]["output_shape"][0])
        logging.debug(
            "Get input shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], input_node[0], input_shape)
        )

        weight_shape = graphe[weight_node[0]]["attr"]["attr"]["tensor_shape"]
        if len(weight_shape) != 4:
            logging.warning(
                "Failed to parse weight shape %s of node %s."
                % (str(weight_shape), node["attr"]["name"])
            )
            logging.debug(node)
            return

        logging.debug(
            "Get weight shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], weight_node, weight_shape)
        )

        k_size = weight_shape[:2]
        cout = weight_shape[3]

        if node["attr"]["attr"]["strides"][::3] != [1, 1]:
            logging.warning(
                "Invalid strides %s of node %s."
                % (str(node["attr"]["attr"]["strides"]), node["attr"]["name"])
            )
            logging.debug(node)
            return

        strides = node["attr"]["attr"]["strides"]
        dilation = node["attr"]["attr"]["dilations"]
        padding = node["attr"]["attr"]["padding"].decode("utf-8")
        logging.debug(
            "Op:%s, stride:%s, dilation:%s, padding:%s."
            % (node["attr"]["name"], str(strides), str(dilation), str(padding))
        )

        kernel_extent_w = ph.get_w(dilation) * (ph.get_w(strides) - 1) + 1
        kernel_extent_h = ph.get_h(dilation) * (ph.get_h(strides) - 1) + 1

        out_shape, padding_shape = ShapeInference.get_padding_shape(
            input_shape, cout, [kernel_extent_w, kernel_extent_h], strides, padding
        )

        node["attr"]["attr"]["kernel_shape"] = copy.deepcopy(k_size)
        node["attr"]["attr"]["dilations"] = copy.deepcopy(
            node["attr"]["attr"]["dilations"][1:-1]
        )
        node["attr"]["attr"]["strides"] = copy.deepcopy(
            node["attr"]["attr"]["strides"][1:-1]
        )
        node["attr"]["attr"]["weight_shape"] = copy.deepcopy(weight_shape)
        node["attr"]["attr"]["pads"] = padding_shape

        return [input_shape], [out_shape]

    @staticmethod
    def DepthwiseConv2dNative_get_shape(graphe, node):
        """
        Get shape of a DepthwiseConv2dNative operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        weight_node = ph.find_weights_root(graphe, node)
        if len(weight_node) != 1:
            logging.warning("Failed to get shape of node %s." % (node["attr"]["name"]))
            logging.debug(node)
            return

        input_node = [x for x in node["inbounds"] if x != weight_node]
        input_node = [x for x in input_node if graphe[x]["attr"]["type"] != "Identity"]
        if len(input_node) != 1:
            logging.warning("Failed to get input node of %s." % (node["attr"]["name"]))
            logging.debug(node)
            return

        input_shape = copy.deepcopy(graphe[input_node[0]]["attr"]["output_shape"][0])
        logging.debug(
            "Get input shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], input_node[0], input_shape)
        )

        weight_shape = graphe[weight_node[0]]["attr"]["attr"]["tensor_shape"]
        if len(weight_shape) != 4:
            logging.warning(
                "Failed to parse weight shape %s of node %s."
                % (str(weight_shape), node["attr"]["name"])
            )
            logging.debug(node)
            return

        logging.debug(
            "Get weight shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], weight_node, weight_shape)
        )

        k_size = weight_shape[:2]
        cin = weight_shape[2]

        if node["attr"]["attr"]["strides"][::3] != [1, 1]:
            logging.warning(
                "Invalid strides %s of node %s."
                % (str(node["attr"]["attr"]["strides"]), node["attr"]["name"])
            )
            logging.debug(node)
            return

        strides = node["attr"]["attr"]["strides"]
        dilation = node["attr"]["attr"]["dilations"]
        padding = node["attr"]["attr"]["padding"].decode("utf-8")

        logging.debug(
            "Op:%s, stride:%s, dilation:%s, padding:%s."
            % (node["attr"]["name"], str(strides), str(dilation), str(padding))
        )

        kernel_extent_w = ph.get_w(dilation) * (ph.get_w(strides) - 1) + 1
        kernel_extent_h = ph.get_h(dilation) * (ph.get_h(strides) - 1) + 1

        out_shape, padding_shape = ShapeInference.get_padding_shape(
            input_shape, cin, [kernel_extent_w, kernel_extent_h], strides, padding
        )

        node["attr"]["attr"]["kernel_shape"] = copy.deepcopy(k_size)
        node["attr"]["attr"]["dilations"] = copy.deepcopy(
            node["attr"]["attr"]["dilations"][1:-1]
        )
        node["attr"]["attr"]["strides"] = copy.deepcopy(
            node["attr"]["attr"]["strides"][1:-1]
        )
        node["attr"]["attr"]["weight_shape"] = copy.deepcopy(weight_shape)
        node["attr"]["attr"]["pads"] = padding_shape

        return [input_shape], [out_shape]

    @staticmethod
    def Reduce_get_shape(graphe, node):
        """
        Get shape of a Reduce operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        input_shape = graphe[node["inbounds"][0]]["attr"]["output_shape"][0]
        output_shape = input_shape
        logging.debug(
            "Get input shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], node["inbounds"][0], output_shape)
        )

        output_shape[1] = 0
        output_shape[2] = 0

        reduction_indices = node["attr"]["attr"]["reduction_indices"]
        logging.debug("Get Reduction Indices %s.", str(reduction_indices))

        reduction_cnt = 0
        for reduction in sorted(reduction_indices):
            del output_shape[reduction - reduction_cnt]
            reduction_cnt += 1

        return [input_shape], [output_shape]

    @staticmethod
    def Mean_get_shape(graphe, node):
        """
        Get shape of a Mean operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Reduce_get_shape(graphe, node)

    @staticmethod
    def GlobalAveragePooling2D_get_shape(graphe, node):
        """
        Get shape of a GlobalAveragePooling2D operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Reduce_get_shape(graphe, node)

    @staticmethod
    def GlobalMaxPooling2D_get_shape(graphe, node):
        """
        Get shape of a GlobalMaxPooling2D operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Reduce_get_shape(graphe, node)

    @staticmethod
    def MatMul_get_shape(graphe, node):
        """
        Get shape of a MatMul operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        weight_node = ph.find_weights_root(graphe, node)
        if len(weight_node) != 1:
            logging.warning("Failed to get shape of node %s." % (node["attr"]["name"]))
            logging.debug(node)
            return

        weight_shape = graphe[weight_node[0]]["attr"]["attr"]["tensor_shape"]
        if len(weight_shape) != 2:
            logging.warning(
                "Failed to parse weight shape %s of node %s."
                % (str(weight_shape), node["attr"]["name"])
            )
            logging.debug(node)
            return

        logging.debug(
            "Get weight shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], weight_node, weight_shape)
        )

        input_node = [x for x in node["inbounds"] if x != weight_node]
        input_node = [x for x in input_node if graphe[x]["attr"]["type"] != "Identity"]
        if len(input_node) != 1:
            logging.warning("Failed to get input node of %s." % (node["attr"]["name"]))
            logging.debug(node)
            return

        input_shape = copy.deepcopy(graphe[input_node[0]]["attr"]["output_shape"][0])
        logging.debug(
            "Get input shape of %s from %s, input shape:%s."
            % (node["attr"]["name"], input_node[0], input_shape)
        )

        if weight_shape[0] != input_shape[1]:
            logging.warning(
                "Weight shape and input shape not matched for %s."
                % (node["attr"]["name"])
            )
            logging.debug(node)
            return

        output_shape = copy.deepcopy(input_shape)
        output_shape[1] = weight_shape[1]

        return [input_shape], [output_shape]

    @staticmethod
    def Reshape_get_shape(graphe, node):
        """
        Get shape of a Reshape operator.
        It normally should take from the shape attibution,
        but we patch it for Pack-StrideSlice-Reshape, and
        prevent the program from dynamic inference.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        if "shape" in node["attr"]["attr"].keys():
            logging.debug(
                "Shape attr find in %s op, propogate with normal.", node["attr"]["name"]
            )
            input_shape = copy.deepcopy(
                graphe[node["inbounds"][0]]["attr"]["output_shape"][0]
            )
            exp_output_shape = copy.deepcopy(node["attr"]["attr"]["shape"])
        else:
            logging.debug(
                "Shape attr not find in %s op, try finding the shape node.",
                node["attr"]["name"],
            )
            for in_node in node["inbounds"]:
                if graphe[in_node]["attr"]["type"] == "Const":
                    exp_output_shape = copy.deepcopy(
                        graphe[in_node]["attr"]["constant"]
                    )
                elif graphe[in_node]["attr"]["type"] == "Pack":
                    exp_output_shape = [1] + [
                        it
                        for sl in graphe[in_node]["attr"]["attr"]["constant"]
                        for it in sl
                    ]
                    logging.debug(
                        "Fetched expected output shape from Pack op %s"
                        % str(exp_output_shape)
                    )
                else:
                    input_shape = copy.deepcopy(
                        graphe[in_node]["attr"]["output_shape"][0]
                    )

        input_elements = abs(reduce(lambda x, y: x * y, input_shape))
        exp_output_shape_elements = abs(reduce(lambda x, y: x * y, exp_output_shape))

        if input_elements != exp_output_shape_elements:
            logging.warning(
                "Input shape %s and output shape %s not matched for %s."
                % (str(input_shape), str(exp_output_shape), node["attr"]["name"])
            )

        return [input_shape], [exp_output_shape]

    @staticmethod
    def Concat_get_shape(graphe, node):
        """
        Get shape of a Concat operator.
        We add up the shape through axis.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        input_shape = []
        for in_node in node["inbounds"]:
            in_shape = graphe[in_node]["attr"]["output_shape"][0]
            if in_shape != []:
                input_shape.append(in_shape)
                logging.debug(
                    "Get input shape of %s from %s, input shape:%s."
                    % (node["attr"]["name"], in_node, input_shape[-1])
                )
        axis = node["attr"]["attr"]["axis"][0]

        output_shape = copy.deepcopy(input_shape[0])
        for in_shape in input_shape[1:]:
            output_shape[axis] += in_shape[axis]

        return copy.deepcopy(input_shape), [output_shape]

    @staticmethod
    def Concatenate_get_shape(graphe, node):
        """
        Get shape of a Concatenate operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Concat_get_shape(graphe, node)

    @staticmethod
    def ConcatV2_get_shape(graphe, node):
        """
        Get shape of a ConcatV2 operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        return ShapeInference.Concat_get_shape(graphe, node)

    @staticmethod
    def Split_get_shape(graphe, node):
        """
        Get shape of a Split operator.
        Also patched for Pack-StrideSlice-Split sequence.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        for in_node in node["inbounds"]:
            if graphe[in_node]["attr"]["type"] == "Const":
                pass
            elif graphe[in_node]["attr"]["type"] == "Pack":
                pass
            else:
                input_shape = copy.deepcopy(graphe[in_node]["attr"]["output_shape"][0])

        split_dim = node["attr"]["attr"]["split_dim"][0]
        logging.debug("Fetched Split dim for %s is %s.", node["attr"]["name"], split_dim)
        output_node_cnt = len(node["outbounds"])

        output_shape = copy.deepcopy(input_shape)
        output_shape[split_dim] = output_shape[split_dim] // output_node_cnt
        output_shape = copy.deepcopy([output_shape]) * output_node_cnt

        return [copy.deepcopy(input_shape)], output_shape

    @staticmethod
    def Transpose_get_shape(graphe, node):
        """
        Get shape of a Transpose operator.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        for in_node in node["inbounds"]:
            if graphe[in_node]["attr"]["type"] == "Const":
                perm = copy.deepcopy(graphe[in_node]["attr"]["attr"]["constant"])
                logging.debug("Fetched perm sequence from Const op %s" % str(perm))
            elif graphe[in_node]["attr"]["type"] == "Pack":
                perm = [1] + [
                    it
                    for sl in graphe[in_node]["attr"]["attr"]["constant"]
                    for it in sl
                ]
                logging.debug("Fetched perm sequence from Pack op %s" % str(perm))
            else:
                input_shape = copy.deepcopy(graphe[in_node]["attr"]["output_shape"][0])
                logging.debug(
                    "Fetched input shape from %s,  %s" % (in_node, str(input_shape))
                )

        exp_output_shape = []
        for i in range(len(perm)):
            exp_output_shape.append(input_shape[perm[i]])

        return [input_shape], [exp_output_shape]

    @staticmethod
    def Packed_get_shape(graphe, node):
        """
        Get shape of a Transpose operator.
        Patched for kernel detector.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        seq = ph.get_graph_seq(graphe, [node["attr"]["name"]])[:5]
        for out_node in seq:
            if graphe[out_node]["attr"]["type"] == "Reshape":
                if "input_shape" in graphe[out_node]["attr"].keys():
                    return (
                        graphe[out_node]["attr"]["input_shape"],
                        graphe[out_node]["attr"]["input_shape"],
                    )
        return [[0, 0, 0, 0]], [[0, 0, 0, 0]]

    @staticmethod
    def StridedSlice_get_shape(graphe, node):
        """
        Get shape of a Transpose operator.
        Patched for kernel detector.

        Parameters
        ----------
        graphe : dict
            The Graph IR in dict format.
        node   : dict
            The node in Graph IR in dict format.
        """
        seq = ph.get_graph_seq(graphe, [node["attr"]["name"]])[:5]
        for out_node in seq:
            if graphe[out_node]["attr"]["type"] == "Reshape":
                if "input_shape" in graphe[out_node]["attr"].keys():
                    return (
                        graphe[out_node]["attr"]["input_shape"],
                        graphe[out_node]["attr"]["input_shape"],
                    )
        return [[0, 0, 0, 0]], [[0, 0, 0, 0]]

    def __init__(self, graphe):
        """
        Take the graph, and append output shape
        and input shape to the attributes of nodes.

        Parameters
        ----------
        graphe : Graphe
            The Graph IR class.
        """
        graph = graphe.get_graph()
        seq = ph.get_graph_seq(graph, graphe.get_graph_head())

        # Pass #1
        for node_name in seq:
            node_get_shape_name = graphe.get_node_type(node_name) + "_get_shape"
            if node_get_shape_name in dir(self):
                input_shape, output_shape = eval("self." + node_get_shape_name)(
                    graph, graph[node_name]
                )
                if output_shape is not None:
                    graph[node_name]["attr"]["output_shape"] = copy.deepcopy(
                        output_shape
                    )
                if input_shape is not None:
                    graph[node_name]["attr"]["input_shape"] = copy.deepcopy(input_shape)
                logging.debug(
                    "Input shape of %s op is %s." % (node_name, str(input_shape))
                )
                logging.debug(
                    "Output shape of %s op is %s." % (node_name, str(output_shape))
                )
            else:
                logging.error("%s not support yet." % graphe.get_node_type(node_name))
                logging.debug("------ node content --------")
                logging.debug(graph[node_name])
                logging.debug("----------------------------")

        # Pass #2
        # This is a patching for back-end, since backend extract shapes from
        # those two ops.
        for node_name in seq:
            if graphe.get_node_type(node_name) in ["Packed", "StridedSlice"]:
                node_get_shape_name = graphe.get_node_type(node_name) + "_get_shape"
                input_shape, output_shape = eval("self." + node_get_shape_name)(
                    graph, graph[node_name]
                )
                if output_shape is not None:
                    graph[node_name]["attr"]["output_shape"] = copy.deepcopy(
                        output_shape
                    )
                if input_shape is not None:
                    graph[node_name]["attr"]["input_shape"] = copy.deepcopy(input_shape)
                logging.debug(
                    "Second Pass: Input shape of %s op is %s."
                    % (node_name, str(input_shape))
                )
                logging.debug(
                    "Second Pass: Output shape of %s op is %s."
                    % (node_name, str(output_shape))
                )
