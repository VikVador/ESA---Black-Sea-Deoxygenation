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
# A simple tool to create and load custom losses
#
# Pytorch
import torch
import torch.nn as nn
import torch.optim as optim

import matplotlib.pyplot as plt

def compute_loss(y_pred : torch.Tensor, y_true : torch.Tensor, problem : str, mask, device : str, kwargs : dict):
    r"""Process data and computes the loss"""

    # Regression (ONLY WORKS FOR ONE DAY ! MUST BE MODIFIED)
    if problem == "regression":

        # Computing the negative log likelihood (element wise)
        error = - y_pred[:, 0, 1,  mask == 1] - ((y_true[:, 0, 0,  mask == 1] - y_pred[:, 0, 0,  mask == 1]) ** 2) / (2 * torch.exp(y_pred[:, 0, 1,  mask == 1]))

        # Summing and averaging over the observed region
        return -torch.nansum(error) / torch.numel(error)

    # Classification
    if problem == "classification":

        # Creation of the weights matrix for the loss, i.e. should be of size (c, 1) where 1 means applied to all samples
        weights = torch.unsqueeze(torch.tensor(kwargs["Loss Weights"]), 1).to(device)

        # Retrieves indices of the observed region
        indices = y_true[0, 0, 0] != -1

        # Reshaping the data to (b, d, c, x * y) (Needed for BCEWithLogitsLoss which only accepts (b, c, x * y) tensors)
        pred = y_pred[:, :, :, indices]
        y    = y_true[:, :, :, indices]

        # Retrieiving dimensions for ease of comprehension
        batch, forecasted_days, classes, xy = pred.shape

        # Reshaping the data (batch * forecasted_days because we compute the loss across all forecasted days for simplicity)
        pred = pred.reshape(batch * forecasted_days, classes, -1)
        y    =    y.reshape(batch * forecasted_days, classes, -1)

        # Metric tools
        loss = torch.nn.BCEWithLogitsLoss(pos_weight = weights)

        # Computing the weighted binary entropy loss function
        return loss(pred, y)
