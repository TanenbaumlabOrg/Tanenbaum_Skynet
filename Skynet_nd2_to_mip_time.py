# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
import nd2
from PIL import Image as im
from os import listdir
from os.path import isfile
import os
from concurrent.futures import ThreadPoolExecutor
import sys
from alive_progress import alive_bar
import numpy as np
import re
import cv2

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "3": Make MIP from .nd2 files. \033[1;37;40m \n')
# Start of inputs
# Location of .nd2 files
print('')
input_path = input('\033[2;37;40mPlease provide the location of the .nd2 files: \033[1;37;40m \n')
# Location of the metadata
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish .png files to be exported: \033[1;37;40m \n')
# Location of the MIP files
print('')
median_maximum = input('\033[2;37;40mDo you wish to make maximum or median projections ("Maximum"/"Median"): \033[1;37;40m \n')
# Determine a substack for MIP
print('')
substack_indicator = input('\033[2;37;40mAny channels from which you only want to project a smaller number of slices ("Yes/No")? \033[1;37;40m \n')
if substack_indicator == 'Yes':
    print('')
    problem_channel= int(input('\033[2;37;40mWhich channel might that be [1,2...N]? \033[1;37;40m \n'))
    print('')
    single_indicator = input('\033[2;37;40mDo you want to take a single slice or still project a subset ("Single/Multiple")? \033[1;37;40m \n')
    if single_indicator == 'Multiple': 
        print('')
        start_z = int(input('\033[2;37;40mIn that channel, what is the bottom z-slice to include [1,2...N]? \033[1;37;40m \n'))
        print('')
        end_z = int(input('\033[2;37;40mIn that channel, what is the top Zslice to include [1,2...N]? \033[1;37;40m \n'))
        sub_z = list(range(start_z-1,end_z))    
    elif single_indicator == 'Single':
        print('')
        single_z = int(input('\033[2;37;40mIn that channel, what is the slice you want to include [1,2...N]? \033[1;37;40m \n'))
        sub_z = single_z-1
    else:
        print('Choose a valid option, idiot.')
        sys.exit()
# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mWhat is the size of your tool today (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]?): \033[1;37;40m \n')
print('')
if number_worker == 'MusclePower':  
    print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
else:
   print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n')
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

# Create metadata folder if not already existing
if not os.path.exists(output_path):
        os.mkdir(output_path)
# End of path information 


# Start defining functions
def make_MIP(input_path, ouput_path, current_base_file, png_names, problem_channel, sub_z):
    
    # Get the Indicator name of current group
    deprecated_name = current_base_file[0:len(current_base_file)-9]
    images_z_slices = [x for x in png_names if re.search(deprecated_name, x)]
    
    
    if f'W0{problem_channel:03}' in deprecated_name:
        if single_indicator == 'Multiple':
            z_positions = len(sub_z)
        else:
            z_positions = 1
    else:
        z_positions = len(images_z_slices)
    # Get number of Z slices
    
    # Load example images to get number XY
    load_name =  '/'.join([input_path,current_base_file])
    base_image = cv2.imread(load_name, cv2.IMREAD_UNCHANGED)
    y_pixel_number, x_pixel_number = base_image.shape[0:2]
    
    # Make empty image to store individual z slices              
    z_image_storage = np.ndarray(shape=(y_pixel_number,x_pixel_number,z_positions), dtype=np.uint16);
            
    for current_z_index in range(z_positions):          
        # Get individual image slice
        if f'W0{problem_channel:03}' in deprecated_name:
            if single_indicator == 'Multiple':
                current_z = sub_z[current_z_index]
            else:
                current_z = sub_z
        else:
            current_z = current_z_index
        current_image_name = images_z_slices[current_z]
        current_load_name = '/'.join([input_path,current_image_name])        
        current_image = cv2.imread(current_load_name, cv2.IMREAD_UNCHANGED)               
        z_image_storage[:,:,current_z_index] = current_image
    
    if median_maximum == 'Maximum':                       
        projection = np.max(z_image_storage,axis = 2)
    elif median_maximum == 'Median':
        median_projection = np.median(z_image_storage,axis = 2)
        projection = np.array(median_projection, dtype='float32').astype('uint16')
    # convert to png
    image_png = im.fromarray(projection)

    # define save name
    save_name_full = '/'.join([output_path,current_base_file])
    image_png.save(save_name_full)

def process_time_points_nd2(output_path, prefix, sub_image_stack, current_xy, z_positions, channels, current_t, time):
    z_string = '\n'.join(['{0:04}'.format(1)])
    time_string = '\n'.join(['{0:04}'.format(current_t + 1)])
    xy_string = '\n'.join(['{0:04}'.format(current_xy + 1)])
    for current_channel in range(channels):
        channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
        sub_channel_stack = sub_image_stack
        
        make_MIP(input_path, output_path, current_base_file, png_names, problem_channel, sub_z)
        

# End of defining functions


# Main body
nd2_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
print('\033[1;34;40mWe identified',str(len(nd2_names)),'unique NIS files. \033[1;37;40m \n')

with alive_bar(len(nd2_names)) as bar: 
    for current_file in nd2_names:       
        dask_image_stack = nd2.imread('/'.join([input_path, current_file]), dask = True)        
        time = len(dask_image_stack.shape) > 5
        prefix, xy_positions = current_file[0:len(current_file) - 4], dask_image_stack.shape[0] if not time else dask_image_stack.shape[1]
        z_positions, channels = dask_image_stack.shape[1:3] if not time else dask_image_stack.shape[2:4]
        time_points = dask_image_stack.shape[0] if time else 0 
        for current_xy in range(xy_positions):
            sub_image_stack = np.asarray(dask_image_stack[:, current_xy, :, :, :, :]) if time else np.asarray(dask_image_stack[current_xy, :, :, :, :])  
            with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
                for current_t in range(time_points):
                    executor.submit(process_time_points_nd2, output_path, prefix, sub_image_stack, current_xy, z_positions, channels, current_t, time)
        bar()
       
# Say goodbye
print('\033[1;34;40mSubroutine "2" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')