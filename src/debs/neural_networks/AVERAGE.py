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
# A neural network definition to be used as emulator
#
import numpy as np
from tools import to_device

# Pytorch
import torch
import torch.nn as nn


class AVERAGE(nn.Sequential):
    r"""A 'neural network' that predicts the pixel temporal average (should be used a baseline)"""

    def __init__(self, data_output : np.array, device : str, kwargs : dict):
        super(AVERAGE, self).__init__()

        # Extracting information
        dataset_size     = kwargs['Dataset Size']
        problem          = kwargs['Problem']
        hypoxia_treshold = kwargs['Hypoxia Treshold']

        # Retrieiving dimensions
        t, x, y = data_output.shape

        # Number of training samples
        train_samples = int(t * dataset_size[0])

        # ----- Regression ------
        if problem == "regression":

            # Determine the minimum and maximum values of the data
            min_value = np.nanmin(data_output)
            max_value = np.nanmax(data_output)

            # Rescale the data to ensure non-negative values
            average_output = data_output + np.abs(min_value) if min_value < 0 else data_output

            # Normalizing the data
            average_output = (average_output - min_value) / (max_value - min_value)

            # Average concentration
            average_output = torch.mean(torch.from_numpy(average_output[: train_samples, :-2, :-2]), dim = 0)

        # ----- Classification ------
        else:

            # Converting to classification
            average_output = torch.from_numpy((data_output[: train_samples, :-2, :-2] < hypoxia_treshold) * 1)

            # Summing over time, i.e. if total number of hypoxic days is greater than 50% of the time, then it is hypoxic
            average_output = (torch.sum(average_output, dim = 0) > train_samples // 2) * 1

            # Conversion to "probabilities", i.e. (t, x, y) to (t, c, x, y) with c = 0 no hypoxia, c = 1 hypoxia
            average_output = torch.stack([(average_output == 0) * 1, average_output]).float()

        # Storing information
        self.outputs = kwargs['Window (Output)']
        self.bs      = kwargs['Batch Size']
        self.average = self.process(average_output)
        self.device  = device

        # Dummy feature (It plays no role whatsoever, it is just a placeholder to make the model work with the trainer)
        self.layer = nn.Conv2d(1, 1, 1)

    def forward(self, x):
        return to_device(self.average[:x.shape[0]], self.device)

    def process(self, x : torch.Tensor):
        r"""Used to format the output to the correct shape"""

        # Adding number of forecasted days
        x = torch.unsqueeze(x, dim = 0) if self.outputs == 1 else \
            torch.stack([x for i in range(self.outputs)], dim = 0)

        # Adding batch size
        return torch.stack([x for i in range(self.bs)], dim = 0)

    def count_parameters(self,):
        r"""Determines the number of trainable parameters in the model"""
        return int(0)