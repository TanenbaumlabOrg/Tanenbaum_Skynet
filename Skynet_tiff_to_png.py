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
import tifffile as tf

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "3": Export .pngs from ome-tiff files. \033[1;37;40m \n')

# Start of inputs
# Location of .nd2 files
print('')
input_path = input('\033[2;37;40mPlease provide the location of the ome-tiff files: \033[1;37;40m \n')
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



def process_channel_tiff(output_path, prefix, current_stack, current_channel, current_t, current_z, current_xy):
    z_string = '\n'.join(['{0:04}'.format(current_z + 1)])
    xy_string = '\n'.join(['{0:04}'.format(current_xy + 1)])
    time_string = '\n'.join(['{0:04}'.format(current_t + 1)])
    channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
    image_png = im.fromarray(current_stack[current_channel,:,:])
    save_name_image = ''.join([prefix, '_', 'P', xy_string, 'T', time_string, 'W', channel_string, 'Z', z_string, '.png'])
    save_name_full = '/'.join([output_path, save_name_image])
    image_png.save(save_name_full)
# Main body
tiff_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
print('\033[1;34;40mWe identified',str(len(tiff_names)),'unique TIFF files. \033[1;37;40m \n')

with alive_bar(len(tiff_names)) as bar:
    for current_file in tiff_names:
        current_stack = tf.imread('/'.join([input_path, current_file]))
        channels = current_stack.shape[0]
        current_t = 0
        current_z = 0
        position_information = current_file[len(current_file)-10:len(current_file)-8]
        position_information_number = int(position_information)
        prefix = current_file[0:len(current_file)-13]
        current_xy = position_information_number - 1
        with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
            for current_channel in range(channels):
                executor.submit(process_channel_tiff,output_path, prefix, current_stack, current_channel, current_t, current_z, current_xy)
bar


       
# Say goodbye
print('\033[1;34;40mSubroutine "3" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')