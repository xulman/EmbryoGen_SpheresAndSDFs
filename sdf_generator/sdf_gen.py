#!/usr/bin/env python3

import torch
import signal
import sys
import os
from math import pi
import time
from collections import OrderedDict # manipulation with state dictionary

# append path for loading generator's own imports
sys.path.append("./sdf_generator")

from lib.device import *
from lib.workspace import *
from lib.decoder import *


def init_network():
    
    print('PyTorch is computing with {}!'.format(device))
    
    # setup   
    experiment_directory = "./sdf_generator/experiments/plat"
    test_epoch = None
    
    specs = load_experiment_specifications(experiment_directory)
    latent_size = specs["CodeLength"]
    
    # load decoder
    decoder = DeepSDF(latent_size, **specs["NetworkSpecs"])
    if device == 'cuda':
        decoder = torch.nn.DataParallel(decoder) 
    if test_epoch is None:
        state_file = 'model.pth'
    else:
        state_file = 'e' + test_epoch.zfill(4) + '_model.pth'
    if device == 'cuda':
        saved_model_state = torch.load(
            os.path.join(experiment_directory, model_params_subdir, state_file))
        decoder.load_state_dict(saved_model_state["model_state_dict"])
    else:
        saved_model_state = torch.load(
            os.path.join(experiment_directory, model_params_subdir, state_file),
            map_location='cpu')
        cpu_state_dict = OrderedDict()
        for k, v in saved_model_state["model_state_dict"].items():
            cpu_state_dict[k.replace("module.", "")] = v
        decoder.load_state_dict(cpu_state_dict)
    if device == 'cuda':
        decoder = decoder.module.to(device)
    else:
        decoder = decoder.to('cpu')
    decoder.eval() # set the dropout and batch norm layers to eval mode
    #print(decoder)
    
    return decoder


# get a single value
def get_sdf_value(x, y, z, t, latent_code, decoder):

    # check input
    assert -1 <= x <= 1, "Space and time coordinates must be in [-1,1]"
    assert -1 <= y <= 1, "Space and time coordinates must be in [-1,1]"
    assert -1 <= z <= 1, "Space and time coordinates must be in [-1,1]"
    assert -1 <= t <= 1, "Space and time coordinates must be in [-1,1]"
    #assert latent_code.shape == (latent_size,), "Incorrect latent code dimensions"
    
    # prepare network inputs
    coordinates = np.array([[x, y, z, t]], dtype=np.float32)
    
    latent_code = latent_code[np.newaxis, ...]
    
    # get sdf value from the network
    sdf_value = decoder(torch.from_numpy(latent_code),
                        torch.from_numpy(coordinates)).detach().cpu()

    return sdf_value.numpy().squeeze().item()


# get multiple values at once
def get_sdf_values(coordinates, latent_code, decoder):

    # check input
    # TODO ??
    
    # prepare network inputs
    latent_code = latent_code[np.newaxis, ...]
    latent_code = torch.from_numpy(latent_code).expand(coordinates.shape[0], -1)
    
    coordinates = torch.from_numpy(coordinates)
    
    # get sdf values from the network
    sdf_values = decoder(latent_code.to(device),
                         coordinates.to(device)).detach().cpu()

    return sdf_values.numpy().squeeze()
    
