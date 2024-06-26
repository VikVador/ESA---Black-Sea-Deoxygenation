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
from .fcnn     import FCNN
from .unet     import UNET
from .average  import AVERAGE


def load_neural_network(architecture : str, data_output : np.array, device : str, kwargs : dict):
    r"""Loads a neural network of a given architecture"""

    # Security
    assert architecture in ["FCNN", "UNET", "AVERAGE"], f"Architecture {architecture} not recognized"

    # Extracting information
    inputs          = kwargs['Inputs']
    problem         = kwargs['Problem']
    windows_inputs  = kwargs['Window (Inputs)']
    windows_outputs = kwargs['Window (Output)']
    windows_transfo = kwargs['Window (Transformation)']
    architecture    = kwargs['Architecture']
    scaling         = kwargs['Scaling']
    kernel_size     = kwargs['Kernel Size']
    batch_size      = kwargs['Batch Size']

    # Stores the number of inputs (3 = mesh & bathymetry)
    nb_inputs = 3

    # Determining the total number of inputs
    for i in ["temperature", "salinity", "chlorophyll", "kshort", "klong"]:
        nb_inputs += 1 if i in inputs else 0

    # Computing last dimensions
    days   = int(np.ceil(windows_inputs/windows_transfo))
    values = 3 if windows_transfo > 1 else 1

    # Final number of inputs
    nb_inputs *= days * values

    # Initialization of neural network and pushing it to device (GPU)
    if architecture == "FCNN":
        return FCNN(inputs = nb_inputs,
               outputs     = windows_outputs,
     window_transformation = windows_transfo,
               scaling     = scaling,
               problem     = problem,
               kernel_size = kernel_size).to(device)

    elif architecture == "UNET":
        return UNET(inputs = nb_inputs,
                   outputs = windows_outputs,
     window_transformation = windows_transfo,
                   scaling = scaling,
                   problem = problem).to(device)

    elif architecture == "AVERAGE":
        return AVERAGE(data_output = data_output,
                            device = device,
                            kwargs = kwargs).to(device)

    else:
        raise ValueError("Unknown architecture")