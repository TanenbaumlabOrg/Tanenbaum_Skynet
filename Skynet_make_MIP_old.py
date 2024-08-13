# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
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
import concurrent.futures
from numba import njit

os.system('color')

def print_colored_message(color_code, message):
    print(f'\033[{color_code}m{message}\033[1;37;40m')

# Welcome Message
print_colored_message('1;34;40', 'You accessed subroutine "4": Make MIPs from .png files.\n')

# Start of inputs
input_path = input('\033[2;37;40mPlease provide the location of the .png files: \033[1;37;40m\n')
output_path = input('\033[2;37;40mPlease provide the location to which you wish MIPs files to be exported: \033[1;37;40m\n')
median_maximum = input('\033[2;37;40mDo you wish to make maximum or median projections ("Maximum"/"Median"): \033[1;37;40m\n')
substack_indicator = input('\033[2;37;40mAny channels from which you only want to project a smaller number of slices ("Yes/No")? \033[1;37;40m\n')

problem_channel, sub_z = 999, 999
if substack_indicator == 'Yes':
    problem_channel = int(input('\033[2;37;40mWhich channel might that be [1,2...N]? \033[1;37;40m\n'))
    single_indicator = input('\033[2;37;40mDo you want to take a single slice or still project a subset ("Single/Multiple")? \033[1;37;40m\n')
    
    if single_indicator == 'Multiple':
        start_z = int(input('\033[2;37;40mIn that channel, what is the bottom z-slice to include [1,2...N]? \033[1;37;40m\n'))
        end_z = int(input('\033[2;37;40mIn that channel, what is the top Zslice to include [1,2...N]? \033[1;37;40m\n'))
        sub_z = list(range(start_z - 1, end_z))
    elif single_indicator == 'Single':
        single_z = int(input('\033[2;37;40mIn that channel, what is the slice you want to include [1,2...N]? \033[1;37;40m\n'))
        sub_z = single_z - 1
    else:
        print('Choose a valid option, idiot.')
        sys.exit()

number_worker = input('\033[2;37;40mHow many proteins did you pack into your device (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m\n')
if number_worker == 'MusclePower':
    print_colored_message('1;34;40', 'Arnie would be proud. Bullets and Peperoni it is.\n')
else:
    print_colored_message('1;34;40', 'The answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please note that the T-800 has been dispatched to eradicate you from the timeline.\n')

# Check path information (consistency)
if not os.path.exists(input_path):
    print_colored_message('1;31;40', 'You are a moron. The path does not exist.\n')
    print_colored_message('1;31;40', 'Try again with the correct path.\n')
    sys.exit()
elif not os.listdir(input_path):
    print_colored_message('1;31;40', 'You are an even bigger moron. There are no files in that directory.\n')
    print_colored_message('1;31;40', 'Try putting it in first.\n')
else:
    print_colored_message('1;33;40', 'For now, we will acknowledge your supremacy and are processing your request. Standby.\n')

# Create MIP folder if not already existing
if not os.path.exists(output_path):
    os.mkdir(output_path)

# Start defining functions
def load_images(input_path, current_name):
    # Load example images to get number XY
    load_name =  '/'.join([input_path,current_name])
    current_image = cv2.imread(load_name, cv2.IMREAD_UNCHANGED)
    return current_image

def save_images(output_path, projection, current_base_file):
    image_png = im.fromarray(projection)
    # define save name
    save_name_full = '/'.join([output_path,current_base_file])
    image_png.save(save_name_full)


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
    base_image = load_images(input_path,current_base_file)
    
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
        current_image = load_images(input_path,current_image_name)                
        z_image_storage[:,:,current_z_index] = current_image
    
    if median_maximum == 'Maximum':                       
        projection = np.max(z_image_storage,axis = 2)
    elif median_maximum == 'Median':
        median_projection = np.median(z_image_storage,axis = 2)
        projection = np.array(median_projection, dtype='float32').astype('uint16')
    
    save_images(output_path, projection, current_base_file)

# Start of main body
png_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]

# Get Groups with same string but different Z 
unique_groups = [x for x in png_names if re.search('Z0001', x)];
number_groups = len(unique_groups);
print('\033[1;34;40mWe identified',str(number_groups),'unique groups with 1 or more z-slices. \033[1;37;40m \n')

with alive_bar(number_groups) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(make_MIP, input_path, output_path, current_base_file, png_names, problem_channel, sub_z) for current_base_file in unique_groups]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task

# Say goodbye
print('\033[1;34;40mSubroutine "4" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')
