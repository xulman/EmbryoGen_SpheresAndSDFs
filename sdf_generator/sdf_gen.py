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
#from lib.utils import *
#from lib.data import *


#main_function("./experiments/plat", "generate")


def init_network():
    network = int(5)
    return network


def get_sdf_value(x, y, z, t, latent_code, network):
    # setup   
    experiment_directory = "./sdf_generator/experiments/plat"
    test_epoch = None
    
    #print('PyTorch is computing with {}!'.format(device))

    specs = load_experiment_specifications(experiment_directory)

    #print("Experiment description: \n" + ' '.join([str(elem) for elem in
    #                                               specs["Description"]]))

    latent_size = specs["CodeLength"]
    num_sequences = specs["NumSequences"]
    # size of one reconstruction batch
    rec_size = specs["ReconstructionSubsetSize"]
    num_frames_per_sequence_to_reconstruct = specs["ReconstructionFramesPerSequence"]
    reconstruction_dims = specs["ReconstructionDims"]
    # use .MAT (False) or .HDF5 (True) to load and save SDFs
    use_hdf5 = specs["UseHDF5"] 
    # gzip compression level: 0 (min) ... 9 (max)
    hdf5_compr = specs["HDF5CompressionLevel"] 

    # check input
    assert -1 <= x <= 1, "Space and time coordinates must be in [-1,1]"
    assert -1 <= y <= 1, "Space and time coordinates must be in [-1,1]"
    assert -1 <= z <= 1, "Space and time coordinates must be in [-1,1]"
    assert -1 <= t <= 1, "Space and time coordinates must be in [-1,1]"
    assert latent_code.shape == (latent_size,), "Incorrect latent code dimensions"
    rot_ang = np.array([0, 0, 0], dtype=np.float32)

    '''def signal_handler(sig, frame):
        print("Stopping early...")
        sys.exit(0)'''

    #signal.signal(signal.SIGINT, signal_handler)

    # load decoder
    decoder = DeepSDF(latent_size, **specs["NetworkSpecs"])
    if device == 'gpu':
        decoder = torch.nn.DataParallel(decoder) 
    if test_epoch is None:
        state_file = 'model.pth'
    else:
        state_file = 'e' + test_epoch.zfill(4) + '_model.pth'
    if device == 'gpu':
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
    #decoder = decoder.module.cuda()
    if device == 'gpu':
        decoder = decoder.module.to(device)
    else:
        decoder = decoder.to('cpu')
    decoder.eval() # set the dropout and batch norm layers to eval mode
    #print(decoder)
                                     
    # prepare normalized time coordinates in [-1, 1]
    '''t = np.asarray([scene for scene in 
                    range(num_frames_per_sequence_to_reconstruct)],
                   dtype='float32')
    t = (t - np.min(t)) / (np.max(t) - np.min(t)) * 2. - 1.
    t = torch.from_numpy(t)'''
    
    
    '''def get_pixel_coords(N):
        # prepare coordinate grid
        pixel_coords = np.stack(np.mgrid[:N[0], :N[1], :N[2]], 
                                axis=-1)[None, ...].astype(np.single)
        pixel_coords[..., 0] = pixel_coords[..., 0] / max(N[0] - 1, 1)
        pixel_coords[..., 1] = pixel_coords[..., 1] / (N[1] - 1)
        pixel_coords[..., 2] = pixel_coords[..., 2] / (N[2] - 1)
        pixel_coords = np.squeeze(pixel_coords)
        
        # normalize from [0, 1] to [-1, 1]
        pixel_coords -= 0.5
        pixel_coords *= 2.  
        
        # flatten all but the last dimension
        pixel_coords = pixel_coords.reshape(-1, pixel_coords.shape[-1])
        
        return pixel_coords'''
    
    '''
    def save_sdf(output_sdf, filename):
        if use_hdf5:
            print('Saving and compressing HDF5 file with gzip level {}...'.format(
                hdf5_compr)) 
            # save 3D+t SDF to HDF5 file
            output_sdf = np.transpose(output_sdf,(3, 2, 1, 0))
            h5file = h5py.File(filename + '.h5', 'w')
            dset = h5file.create_dataset("sdf_vid", shape=output_sdf.shape,
                                         data=output_sdf,
                                         fillvalue=0.0,
                                         chunks=(output_sdf.shape[0],
                                                 output_sdf.shape[1],
                                                 output_sdf.shape[2],
                                                 1),
                                         dtype=np.float32,
                                         compression='gzip',
                                         compression_opts=hdf5_compr)
            h5file.close()
            print('Saved ' + filename + '.h5')  
        
        else:
            # save 3D+t SDF to matlab file
            sio.savemat(filename + '.mat', {'sdf_vid':output_sdf})
            print('Saved ' + filename + '.mat')
    '''

    # Generate (new shapes) ###################################################
        
    '''def create_SDF(decoder, latent_vec, time, rot_ang, pixel_coords, 
                   N=[128,128,128], max_batch=64**3, offset=None, 
                   scale=None):'''
    
    coordinates = np.array([[x, y, z, t]], dtype=np.float32)

    # pre-allocate array
    '''num_samples = N[0]*N[1]*N[2] 
    samples = torch.zeros(num_samples, 5, dtype=torch.float32, requires_grad=False)
    
    # rotate cootdinates
    pixel_coords = torch.from_numpy(pixel_coords) @ \
        euler_angles_to_matrix(torch.from_numpy(rot_ang), 'XYZ')
    
    # paste grid into the samples array
    samples[:, 0:3] = pixel_coords
    samples[:, 3] = time.expand(num_samples)

    # infer SDF samples    
    head = 0
    while head < num_samples:
        sample_subset = samples[head : min(head + max_batch, num_samples), 0:4].to(device)
        samples[head : min(head + max_batch, num_samples), 4] = \
            decode_sdf(decoder, latent_vec, sample_subset).squeeze(1).detach().cpu()
        head += max_batch
    
    # reshape SDF
    sdf_values = samples[:, 4].reshape(
        N[0], N[1], N[2]).detach().cpu().numpy().astype(np.float32)'''
    #print('min:', np.min(sdf_values),
    #      'max:', np.max(sdf_values),'\n')
    
    '''sdf_value = decode_sdf(decoder, latent_code, coordinates).detach().cpu()
    
    def decode_sdf(decoder, latent_vector, coordinates):
        num_samples = coordinates.shape[0]
        latent_repeat = latent_vector.expand(num_samples, -1)
        sdf = decoder(latent_repeat, coordinates)
        return sdf'''
    
    latent_code = latent_code[np.newaxis, ...]
    sdf_value = decoder(torch.from_numpy(latent_code),
                        torch.from_numpy(coordinates)).detach().cpu()
    
    # convert tensor to python float
    sdf_value = sdf_value.numpy().squeeze().item()

    return sdf_value
                
            
    ###########################################################################
        
    print("\nDone!")

'''if __name__ == "__main__":
    
    x = 0
    y = 0
    z = 0
    t = 0
    
    # randomly generate a latent vector
    latent_code = np.random.normal(0.0, 0.001, size=(64)).astype(np.float32)

    sdf_value = get_sdf_value(x, y, z, t, latent_code)
        
    print("\nSDF value: {}".format(sdf_value))'''

    
    
