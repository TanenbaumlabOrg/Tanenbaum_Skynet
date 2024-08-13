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


os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "7": Correct inhomogenous illumination by using acquired flatfield images. \033[1;37;40m \n')

# Start of inputs
# Location of .png files
print('')
input_path = input('\033[2;37;40mPlease provide the location of files you wish to correct for inhomogenous illumination (and which will be used to calculate the illumination function): \033[1;37;40m \n')
# Location of the MIP files
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish the illumination corrected files to be exported: \033[1;37;40m \n')
# Location of the MIP files
print('')
flatfield_path = input('\033[2;37;40mPlease provide the location of the flatfield images used for correction: \033[1;37;40m \n')
print('\033[2;37;40mEnsure that the flatfield images have the naming convection with "W000X" with X being the correct mapping of images to flatfields. \033[1;37;40m \n')
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
    print(print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n'))
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
elif not os.path.exists(flatfield_path):
    print('')
    print('\033[1;31;40mYou are a moron. The path does not exist. \033[1;37;40m \n')
    print('\033[1;31;40mTry again with the correct path. \033[1;37;40m \n')
    sys.exit()
elif len(os.listdir(flatfield_path)) == 0:    
    print('')
    print('\033[1;31;40mYou are an even bigger moron. There are no files in that directory. \033[1;37;40m \n')
    print('\033[1;31;40mTry putting it in first. \033[1;37;40m \n')
else:
    print('')
    print('\033[1;33;40mFor now, we will acknowledge your supremacy and are processing your request. Standby. \033[1;37;40m \n')
# end of path information

# Create illumination correction folder if not already existing
if not os.path.exists(output_path):
        os.mkdir(output_path)
  

# Start of defining functions
def correct_illumination(input_path, output_path, current_file, converted_correction_image):    
    
    current_image_to_correct = cv2.imread('/'.join([input_path,current_file]),cv2.IMREAD_UNCHANGED)
    corrected_image = np.round(np.divide(current_image_to_correct,converted_correction_image))
    corrected_image[corrected_image > 65535] = 65535
    image_png = im.fromarray(np.array(corrected_image, dtype='float64').astype('uint16'));
    # define save name
    save_name_full = '/'.join([output_path,current_file])
    image_png.save(save_name_full)
# End of defining functions 

# Main Body

# Get names of all MIPs (.png) files in the specified folder
mip_names = [current_file for current_file in listdir(input_path) if isfile(join(input_path,current_file))];
numper_mip = np.shape(mip_names)[0];
flatfield_names = [current_file for current_file in listdir(flatfield_path) if isfile(join(flatfield_path,current_file))];

print('\033[1;34;40mWe identified',str(len(mip_names)),'unique files to correct for illumination. \033[1;37;40m \n')
       
# Main Body
with alive_bar(number_channel) as bar:    
    for current_channel in range(number_channel):
    
        # Get Images with that wavelength
        images_channel = [x for x in mip_names if re.search(f'W0{current_channel+1:03}', x)]
        number_with_channel = len(images_channel);
        
        # Get Flatfield with that wavelength
        image_flatfield = [x for x in flatfield_names if re.search(f'W0{current_channel+1:03}', x)]
        
        correction_image = cv2.imread(join(flatfield_path,image_flatfield[0]),cv2.IMREAD_UNCHANGED)
        converted_correction_image = correction_image/np.mean(correction_image)
        
        # Now correct each image individual and write
        with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
            for current_file in images_channel:
                executor.submit(correct_illumination, input_path, output_path, current_file, converted_correction_image)
    
        bar()

# Say goodbye
print('\033[1;34;40mSubroutine "7" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')