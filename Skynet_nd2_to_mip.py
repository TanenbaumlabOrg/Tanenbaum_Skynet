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

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "3": Export .png from .nd2 files. \033[1;37;40m \n')

# Start of inputs
# Location of .nd2 files
print('')
input_path = input('\033[2;37;40mPlease provide the location of the .nd2 files: \033[1;37;40m \n')
# Location of the metadata
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish .png files to be exported: \033[1;37;40m \n')
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
def process_z_position_nd2(output_path, prefix, sub_image_stack, current_xy, current_z, channels, time_points, time):
    z_string = '\n'.join(['{0:04}'.format(current_z + 1)])
    xy_string = '\n'.join(['{0:04}'.format(current_xy + 1)])
    for current_channel in range(channels):
        channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
        for current_t in range(time_points) if time else [0]:
            time_string = '\n'.join(['{0:04}'.format(current_t + 1)])
            # ImagePNG = im.fromarray(CurrentImageStack[CurrentT, CurrentXY, CurrentZ, CurrentChannel, :, :]) if Time else im.fromarray(CurrentImageStack[CurrentXY, CurrentZ, CurrentChannel, :, :])
            image_png = im.fromarray(sub_image_stack[current_t, current_z, current_channel, :, :]) if time else im.fromarray(sub_image_stack[current_z, current_channel, :, :])
            save_name_image = ''.join([prefix, '_', 'P', xy_string, 'T', time_string, 'W', channel_string, 'Z', z_string, '.png'])
            save_name_full = '/'.join([output_path, save_name_image])
            image_png.save(save_name_full)
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
                for current_z in range(z_positions):
                    executor.submit(process_z_position_nd2, output_path, prefix, sub_image_stack, current_xy, current_z, channels, time_points, time)
        bar()
       
# Say goodbye
print('\033[1;34;40mSubroutine "2" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')