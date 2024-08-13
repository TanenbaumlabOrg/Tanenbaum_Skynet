# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
from os import listdir
from os.path import isfile
import os
import sys
from alive_progress import alive_bar
import numpy as np
import re
from PIL import Image as im
from cellpose import models
from cellpose.io import imread

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "13": Do cellpose segmentation of cells. \033[1;37;40m \n')

# Start of inputs
# Location where input folders are located
print('')
input_path = input('\033[2;37;40mPlease provide the location of images from which you want to use for segmentation: \033[1;37;40m \n')
# Location where output is saved
print('')
output_path = input('\033[2;37;40mPlease provide the location of where segmentation should saved to: \033[1;37;40m \n')
# Nucleus channel
print('')
nucleus_channel = int(input('\033[2;37;40mPlease indicate on which channel nucleus segmentation should be performed [1,2,... N]: \033[1;37;40m \n'))
# Nucleus channel
print('')
cell_channel = int(input('\033[2;37;40mPlease indicate on which channel cell segmentation should be performed [1,2,... N]: \033[1;37;40m \n'))
# Suspected diameter
print('')
diameter_center = int(input('\033[2;37;40mWhat is the average diameter of your objects (in pixel)? \033[1;37;40m \n'))
# model type
print('')
model_type = input('\033[2;37;40mWhich model type do you want to use ("nuclei","cyto","cyto2"? \033[1;37;40m \n')
# Whether to use GP
print('')
gpu_indicator = input('\033[2;37;40mDo you have a massive GPU and want to use it ("Yes/"No")? \033[1;37;40m \n')
if gpu_indicator == 'Yes':
    use_gpu = True
else:
    use_gpu = False
# End of inputs

# Check path information (consistency)
if not os.path.exists(input_path):
    print('')
    print('\033[1;31;40mYou are a moron. The path does not exist. \033[1;37;40m \n')
    print('\033[1;31;40mTry again with the correct path. \033[1;37;40m \n')
    sys.exit()
elif len(os.listdir(input_path)) == 0:    
    print('')
    print('\033[1;31;40mYou are an even bigger moron. There are no files in that directory. \033[1;37;40m \n')
    print('\033[1;31;40mTry putting it in first. \033[1;37;40m \n')
else:
    print('')
    print('\033[1;33;40mFor now, we will acknowledge your supremacy and are processing your request. Standby. \033[1;37;40m \n')

# Create MIP folder if not already existing
if not os.path.exists(output_path):
        os.mkdir(output_path)
# end of file consistency

# define function
def run_cellpose(segmentation_image, diameter, channels, model):
    
    mask, __, __, __ = model.eval(segmentation_image, diameter=diameter, channels=channels, batch_size=64)
    return mask

def prepare_image(input_path,current_nucleus_file,current_cell_file):
    
    prefix = current_nucleus_file[0:len(current_nucleus_file)-4]
    current_nucleus_image = imread('/'.join([input_path,current_nucleus_file]))
    current_cell_image = imread('/'.join([input_path,current_cell_file]))
    y_pixel_number, x_pixel_number = np.shape(current_nucleus_image)
    segmentation_image = np.ndarray(shape=(y_pixel_number,x_pixel_number,2), dtype=np.uint16);
    segmentation_image[:,:,0] = current_cell_image
    segmentation_image[:,:,1] = current_nucleus_image
    
    return segmentation_image, prefix
    
def save_cell_mask(output_path, mask, prefix):
    
    png_masks = im.fromarray(mask)
    mask_save_name = ''.join([output_path,'/',prefix,'_cell.png'])
    png_masks.save(mask_save_name)
    
def run_segmentation(input_path, output_path, current_nucleus_file, current_cell_file,diameter, channels, model):
    
    segmentation_image, prefix = prepare_image(input_path,current_nucleus_file, current_cell_file)
    mask = run_cellpose(segmentation_image, diameter, channels, model)
    save_cell_mask(output_path, mask, prefix)
# end of defining functions


# Main Body
image_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
nucleus_images = [x for x in image_names if re.search(f'W0{nucleus_channel:03}', x)] 
cell_images = [x for x in image_names if re.search(f'W0{cell_channel:03}', x)] 
channels = [0,1]

print('\033[1;34;40mWe identified',str(len(nucleus_images)),'unique groups to segment. \033[1;37;40m \n')

test_model = model_type
model = models.Cellpose(gpu = use_gpu, model_type = test_model)

with alive_bar(len(nucleus_images)) as bar:   
    for current_index in range(len(nucleus_images)):
        current_nucleus_file = nucleus_images[current_index]
        current_cell_file = cell_images[current_index]
        run_segmentation(input_path, output_path, current_nucleus_file, current_cell_file, diameter_center, channels, model)
   
        bar()
            
            
# Say goodbye
print('\033[1;34;40mSubroutine "13" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')

