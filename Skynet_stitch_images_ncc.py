# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""

import numpy as np
from PIL import Image as im
from os import listdir
from os.path import isfile, join
import os
import re
import cv2
import sys
from concurrent.futures import ThreadPoolExecutor
import m2stitch
import contextlib

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "9": Stitch individual images using normalized cross correlation. \033[1;37;40m \n')

## Start of inputs
# Location of files to be stitched
print('')
input_path = input('\033[2;37;40mPlease provide the location of files you wish to stitch: \033[1;37;40m \n')
# Location of stitched files
print('')
output_path = input('\033[2;37;40mPlease provide the location where you want stitched files to be saves: \033[1;37;40m \n')
# Number of channels to correct
print('')
number_channel = int(input('\033[2;37;40mPlease provide the number of channels which need to be stitched: \033[1;37;40m \n'))
# Reference channel to calculate stitching
print('')
reference_channel = int(input('\033[2;37;40mPlease provide the reference channel from which stitching parameters will be calculated: \033[1;37;40m \n'))
# How many rows were acquired in the experiment?
print('')
acquired_rows = int(input('\033[2;37;40mPlease provide the number of rows which were acquired: \033[1;37;40m \n'))
# How many columns were acquired in the experiment?
print('')
acquired_columns = int(input('\033[2;37;40mPlease provide the number of columns which were acquired: \033[1;37;40m \n'))
# determine snake or normal acquisition
print('')
acquisition_type = input('\033[2;37;40mHow were images acquired - in Snake or Normal mode: \033[1;37;40m \n')
# determine snake or normal acquisition
print('')
number_time_points = int(input('\033[2;37;40mHow many time points were acquired: \033[1;37;40m \n'))
# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mHow many of your resources you wish to employ to explore your wildest fantasies (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
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

# Create folder for stitched images if not existing
if not os.path.exists(output_path):
        os.mkdir(output_path)


# Define functions
def stitch_channel(input_path, output_path, illcorr_names, sub_string, current_channel, current_time_point, size_y, size_x, result_df):
    
    current_group_to_correct = [x for x in illcorr_names if re.search(f'W0{current_channel+1:03}', x)]
    images_group_to_correct_pre = [x for x in current_group_to_correct if re.search(sub_string, x)]
    images_group_to_correct = [x for x in images_group_to_correct_pre if re.search(f'T0{current_time_point+1:03}', x)]
    
    empty_image = np.array([cv2.imread('/'.join([input_path, img]), cv2.IMREAD_UNCHANGED) for img in images_group_to_correct], dtype='uint16')

    stitched_image_size = (
        result_df["y_pos2"].max() + size_y,
        result_df["x_pos2"].max() + size_x,
    )
    
    stitched_image = np.zeros_like(empty_image, shape=stitched_image_size)
    
    for i, row in result_df.iterrows():
        stitched_image[
            row["y_pos2"] : row["y_pos2"] + size_y,
            row["x_pos2"] : row["x_pos2"] + size_x,
        ] = empty_image[i]

    image_png = im.fromarray(stitched_image)
    save_name_full = '/'.join([output_path, images_group_to_correct[0]])
    image_png.save(save_name_full)

def calculate_stitch(reference_group, current_group, current_time_point, input_path, output_path):
    
    # Get just relevant string parts
    sub_string = current_group[:-24]

    # Find all images belonging to this group
    images_group_pre = [x for x in reference_group if re.search(sub_string, x)]
    images_group = [x for x in images_group_pre if re.search(f'T0{current_time_point+1:03}', x)]
    
    
    # Load into image stack
    empty_image = np.array([cv2.imread('/'.join([input_path, current_image]), cv2.IMREAD_UNCHANGED) for current_image in images_group])
    
    # Convert to 16bit image
    bit_image = empty_image.astype('uint16')
    
    # Try stitching with different Thresholds
    for ncc_threshold in (0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.075, 0.05, 0.025, 0.01, 0.005):
        try:
            result_df, _ = m2stitch.stitch_images(bit_image, row_index, column_index, row_col_transpose=False, ncc_threshold=ncc_threshold)
            break
        except Exception:
            pass
        else:
            raise RuntimeError('Failed with unknown exception. Vogel. Vollhorst.')

    # Generate the y_pos2 and x_pos2 variables
    result_df["y_pos2"] = result_df["y_pos"] - result_df["y_pos"].min()
    result_df["x_pos2"] = result_df["x_pos"] - result_df["x_pos"].min()
    
    # Get size of the base images
    size_y, size_x = bit_image.shape[1:3]
        
    for current_channel in range(number_channel):
        stitch_channel(input_path, output_path, illcorr_names, sub_string, current_channel, current_time_point, size_y, size_x, result_df)
# end of defining functions
   
# Main code body


# Get important num
sum_positions = acquired_rows * acquired_columns
number_digits = len(str(sum_positions))

# Make TileIndex
tile_index = [int(current_tile) for current_tile in range(1, sum_positions + 1)]

# Make RowIndex
row_index = [int(current_row) for current_row in range(1, acquired_rows + 1) for _ in range(acquired_columns)]

# Make ColumnIndex
column_index = [
    int((current_column - (acquired_columns + 1)) * -1) if acquisition_type == 'Snake' and current_row % 2 == 0 else int(current_column)
    for current_row in range(1, acquired_rows + 1)
    for current_column in range(1, acquired_columns + 1)
]

# Get names of all png files in the specified folder
illcorr_names = [current_file for current_file in listdir(input_path) if isfile(join(input_path,current_file))];
number_illcorr = np.shape(illcorr_names)[0];

# Get all images with the reference channel
reference_group = [x for x in illcorr_names if re.search(f'W0{reference_channel:03}', x)]

# Get the relevant group names
# temp fix
current_group_real = [x for x in reference_group if re.search('P0001', x)]; ## CHANGE TO P0001 again
number_groups = np.shape(current_group_real)[0];

if number_time_points > 1:
    number_groups = 1

# Now get Time Points

# Actual Loop
#with alive_bar(NumberGroups) as bar:
with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:        
    # Submit all tasks to the executor at once
    if number_groups > 1:    
        for current_group in current_group_real:
            with contextlib.redirect_stdout(None):
                executor.submit(calculate_stitch, reference_group, current_group, number_time_points-1, input_path, output_path)
    elif number_time_points > 1:
        for current_time_point in range(number_time_points):
            with contextlib.redirect_stdout(None):
                executor.submit(calculate_stitch, reference_group, current_group_real[0], current_time_point, input_path, output_path)
        # Wait for all tasks to complete
        #for Future in concurrent.futures.as_completed(Futures):
            #bar()  # Update progress bar for each completed task
        
# Say goodbye
print('\033[1;34;40mSubroutine "9" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')
