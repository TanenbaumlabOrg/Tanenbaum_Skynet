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
from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor
from basicpy import BaSiC



os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "5": Correct inhomogenous illumination from MIPs by estimation the illumination function from the data. \033[1;37;40m \n')

# Start of inputs
# Location of .png files
print('')
input_path = input('\033[2;37;40mPlease provide the location of files you wish to correct for inhomogenous illumination (and which will be used to calculate the illumination function): \033[1;37;40m \n')
# Location of the illumination corrected files
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish the illumination corrected files to be exported: \033[1;37;40m \n')
# Location of the flatfield images
print('')
correction_path = input('\033[2;37;40mPlease provide the location to which you wish flat and darkfield files to be exported to: \033[1;37;40m \n')
# Number of channels to correct
print('')
number_channel = int(input('\033[2;37;40mPlease provide the number of channels which were acquired: \033[1;37;40m \n'))
# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mHow much of your power are you willing to invest for this task (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
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

# Create illumination correction folder if not already existing
if not os.path.exists(output_path):
        os.mkdir(output_path)
# end of path information

# Start defining functions
def save_illumination(input_path, output_path, current_file_index, corrected_images, images_channel):    
    
    current_file = images_channel[current_file_index]
    current_corrected_image = corrected_images[current_file_index,:,:]
    current_corrected_image[current_corrected_image > 65535] = 65535
    image_png = im.fromarray(np.array(current_corrected_image, dtype='float32').astype('uint16'));   
    # define save name
    save_name_full = '/'.join([output_path,current_file])
    image_png.save(save_name_full)
  
    
def make_correction(images_channel, current_channel, number_with_channel, y_pixel_number, x_pixel_number):   
    
    basic = BaSiC(get_darkfield=True, smoothness_flatfield=1)
    #ILLCORRStorage = np.ndarray(shape=(YPixelNumber,XPixelNumber,NumberWithChannel),dtype=np.uint16)
    illcorr_storage = np.ndarray(shape=(number_with_channel,y_pixel_number,x_pixel_number),dtype=np.uint16)
    for current_file_index in range(number_with_channel):

        # Load individual image
        current_load_name = '/'.join([input_path,images_channel[current_file_index]])
        current_image = cv2.imread(current_load_name,cv2.IMREAD_UNCHANGED)
        
        

        # Stick into big matrix
        illcorr_storage[current_file_index,:,:] = current_image;   
        #ILLCORRStorage:,:,CurrentFileIndex] = CurrentImage;  
    
    basic.fit(illcorr_storage)
    flatfield_image = basic.flatfield
    darkfield_image = basic.darkfield
    corrected_images = basic.transform(illcorr_storage)
    channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
    full_flatfield_path = ''.join([correction_path,'/','flatfield_W',channel_string,'.npy'])
    full_darkfield_path = ''.join([correction_path,'/','darkfield_W',channel_string,'.npy'])
    np.save(full_flatfield_path,flatfield_image)
    np.save(full_darkfield_path,darkfield_image)
    
    #save_name_full = '/'.join([output_path,current_file])
    
    return corrected_images
# End of defining functions    

# Main Body

# Get names of all MIPs (.png) files in the specified folder
mip_names = [current_file for current_file in listdir(input_path) if isfile(join(input_path,current_file))];
number_mip = np.shape(mip_names)[0];

with alive_bar(number_channel) as bar:    
    for current_channel in range(number_channel):
    
        # Get Images with that wavelenght
        images_channel = [x for x in mip_names if re.search(f'W0{current_channel+1:03}', x)]
        number_with_channel = len(images_channel);
    
        # Load example image to get dimensions
        example_image_name = images_channel[0]
        load_name_example = '/'.join([input_path,example_image_name])
        example_image = cv2.imread(load_name_example,cv2.IMREAD_UNCHANGED)
        y_pixel_number, x_pixel_number = example_image.shape
                       
        corrected_images = make_correction(images_channel, current_channel, number_with_channel, y_pixel_number, x_pixel_number)       
        # Now save every image individually
        with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
            for current_file_index in range(number_with_channel):
                executor.submit(save_illumination, input_path, output_path, current_file_index, corrected_images, images_channel)
    
        bar()

# Say goodbye
print('\033[1;34;40mSubroutine "5" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')

