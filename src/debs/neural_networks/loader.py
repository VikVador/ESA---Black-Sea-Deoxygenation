# -------------------------------------------------------
#
#        |
#       / \
#      / _ \                  ESA - PROJECT
#     |.o '.|
#     |'._.'|          BLACK SEA DEOXYGENATION EMULATOR
#     |     |
#   ,'|  |  |`.             BY VICTOR MANGELEER
#  /  |  |  |  \
#  |,-'--|--'-.|                2023-2024
#
#
# -------------------------------------------------------
#
# Documentation
# -------------
# A simple tool to load neural networks
#
import numpy as np

# Custom libraries
from .unet    import TimeResidual_UNET
from .average import AVERAGE


def load_neural_network(architecture : str, data_output : np.array, device : str, kwargs : dict):
    r"""Loads a neural network of a given architecture"""

    # Security
    assert architecture in ["UNET", "AVERAGE"], f"Architecture {architecture} not recognized"

    # Extracting information
    architecture    = kwargs['Architecture']
    windows_inputs  = kwargs['Window (Inputs)']
    window_output   = kwargs['Window (Outputs)']
    frequencies     = kwargs['Frequencies']
    scaling         = kwargs['Scaling']

    # Total number of inputs (4 physical variables * windows_inputs + bathymetry (1) + mesh (2))
    nb_inputs = windows_inputs * 4 + 3

    # Predicting the mean and log(var)
    window_output = window_output * 2

    # Neural Network
    if architecture == "UNET":
        return TimeResidual_UNET(input_channels = nb_inputs, output_channels = window_output, frequencies = frequencies, scaling = scaling)

    elif architecture == "AVERAGE":
        return AVERAGE(data_output = data_output, device = device, kwargs = kwargs)

    else:
        raise ValueError("Unknown architecture")