# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
from PIL import Image as im
from os import listdir
from os.path import isfile
import os
import sys
from alive_progress import alive_bar
import re
import cv2
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "8": Subtract a flat background value from images. \033[1;37;40m \n')

# Start of inputs
# Location of .png files
print('')
input_path = input('\033[2;37;40mPlease provide the location of the .png files you want to subtract the background from: \033[1;37;40m \n')
# Save location for background substracted files
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish background subtracted .png files to be saved: \033[1;37;40m \n')

# number of wavelength to correct background for....
print('')
channel_input_number = int(input('\033[2;37;40mFrom how many channels subtract a flat background [1,2...N] (Currently restricted to from 1 to N, and cannnot choose only what you need): \033[1;37;40m \n'))
# background per channel
background_list = []
for current_channel in range(channel_input_number):
    print('')
    channel_background = input('\033[2;37;40mIn order, choose the background (int) for the channels: \033[1;37;40m \n')
    background_list.append(channel_background)

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

       
def subtract_background(output_path,input_path,current_file,current_background):
    current_image = cv2.imread('/'.join([input_path,current_file]), cv2.IMREAD_UNCHANGED) 
    current_image[current_image < current_background] = current_background
    background_subtracted = current_image - current_background
    image_png = im.fromarray(background_subtracted)
    save_name = '/'.join([output_path,current_file])
    image_png.save(save_name)
# End of defining functions

# Main body

# Start of main body
png_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]

# Get Groups with same string but different Z 
unique_groups = [x for x in png_names if re.search('W0001', x)];
number_groups = len(unique_groups);
print('\033[1;34;40mWe identified',str(number_groups),'unique groups with 1 or more z-slices. \033[1;37;40m \n')

for current_channel in range(channel_input_number):
    channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
    unique_groups = [x for x in png_names if re.search(channel_string, x)];
    current_background = int(background_list[current_channel])
    with alive_bar(len(unique_groups)) as bar:
        with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
            # Submit all tasks to the executor at once
            Futures = [executor.submit(subtract_background,output_path,input_path,current_file,current_background) for current_file in unique_groups]

            # Wait for all tasks to complete
            for Future in concurrent.futures.as_completed(Futures):
                bar()  # Update progress bar for each completed task

# Say goodbye
print('\033[1;34;40mSubroutine "8" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')