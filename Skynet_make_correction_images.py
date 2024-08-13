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
import cv2


os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "6": Make the cropped images used for illumination correction. \033[1;37;40m \n')

# Start of inputs
# Location of full camera files
print('')
input_path = input('\033[2;37;40mPlease provide the location of the full camera flatfield images: \033[1;37;40m \n')
# Location of the cropped files
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish cropped images should exported: \033[1;37;40m \n')

print('')
y_pixel= int(input('\033[2;37;40mState the dimension of the ROI in Y-dimension: \033[1;37;40m \n'))
print('')
x_pixel= int(input('\033[2;37;40mState the dimension of the ROI in X-dimension: \033[1;37;40m \n'))
print('')
left_offset= int(input('\033[2;37;40mState the offset in pixels from left: \033[1;37;40m \n'))
print('')
top_offset= int(input('\033[2;37;40mState the offset in pixels from top: \033[1;37;40m \n'))


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

# Start of main body
flatfield_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
number_flatfields = len(flatfield_names)

print('\033[1;34;40mWe identified',str(number_flatfields),'unique full camera flatfields. \033[1;37;40m \n')
with alive_bar(number_flatfields) as bar:
    for current_file in flatfield_names:
        current_load_name = '/'.join([input_path,current_file])
        current_image = cv2.imread(current_load_name,cv2.IMREAD_UNCHANGED)
        cropped_image = current_image[(top_offset-1):(top_offset + y_pixel -1),(left_offset-1):(left_offset + x_pixel -1)]
        image_png = im.fromarray(cropped_image)
        current_save_name = '/'.join([output_path,current_file])
        image_png.save(current_save_name)
        
        bar()


# Say goodbye
print('\033[1;34;40mSubroutine "6" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')