# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
from PIL import Image as im
from os import listdir
from os.path import isfile
import os
from alive_progress import alive_bar
import re
import cv2
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "21": Rename Cellprofiler images for stitching. \033[1;37;40m \n')

# Start of inputs
# Location of full camera files
print('')
input_path = input('\033[2;37;40mPlease provide the location of images to be renamed: \033[1;37;40m \n')
# Location of the cropped files
print('')
output_path = input('\033[2;37;40mPlease provide the location to which renamed files to be exported: \033[1;37;40m \n')

# Ending of Blobs
print('')
blob_ending = input('\033[2;37;40mPlease state the exact ending of the Blob images (likely "_Blob.tiff"): \033[1;37;40m \n')
# New channel number for the blobs
print('')
blob_channel_number = int(input('\033[2;37;40mWhich channel number should the blob images get [1,2....N]: \033[1;37;40m \n'))

# Ending of PreBlobs
print('')
preblob_ending = input('\033[2;37;40mPlease state the exact ending of the PreBlob images (likely "_PreBlob.tiff"): \033[1;37;40m \n')
# New channel number for the preblobs
print('')
preblob_channel_number = int(input('\033[2;37;40mWhich channel number should the preblob images get [1,2....N]: \033[1;37;40m \n'))

# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mFinally, how big is your tool (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
print('')
if number_worker == 'MusclePower':  
    print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
else:
   print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n')

# start of defining functions
def rename_blobs(current_file, input_path, output_path, blob_ending, blob_channel_number):
    current_load_name = '/'.join([input_path,current_file])
    current_image = cv2.imread(current_load_name, cv2.IMREAD_UNCHANGED)
    
    deprecated_name = current_file[0:len(current_file)-len(blob_ending)-10]
    new_channel_string = '\n'.join(['{0:04}'.format(blob_channel_number)])
    new_name = ''.join([deprecated_name,'W',new_channel_string,'Z0001.png'])
    
    image_png = im.fromarray(current_image)
    
    current_save_name = '/'.join([output_path,new_name])
    image_png.save(current_save_name)
    
def rename_preblobs(current_file, input_path, output_path, preblob_ending, preblob_channel_number):
    current_load_name = '/'.join([input_path,current_file])
    current_image = cv2.imread(current_load_name, cv2.IMREAD_UNCHANGED)
    
    deprecated_name = current_file[0:len(current_file)-len(preblob_ending)-10]
    new_channel_string = '\n'.join(['{0:04}'.format(preblob_channel_number)])
    new_name = ''.join([deprecated_name,'W',new_channel_string,'Z0001.png'])
    
    image_png = im.fromarray(current_image)
    
    current_save_name = '/'.join([output_path,new_name])
    image_png.save(current_save_name)

# end of defining functions
    
# MainBody
# find all images
image_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
#find blob images
blob_names = [x for x in image_names if re.search(blob_ending, x)];
preblob_names = [x for x in image_names if re.search(preblob_ending, x)];

number_blob_names = len(blob_names)   
number_preblob_names = len(preblob_names)

print('\033[1;34;40mWe identified',str(number_blob_names),'Blob Image files with that channel index. \033[1;37;40m \n') 
    
with alive_bar(number_blob_names) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(rename_blobs, current_file, input_path, output_path, blob_ending, blob_channel_number) for current_file in blob_names]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task

print('\033[1;34;40mWe identified',str(number_preblob_names),'PreBlob Image files with that channel index. \033[1;37;40m \n') 
    
with alive_bar(number_preblob_names) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(rename_preblobs, current_file, input_path, output_path, preblob_ending, preblob_channel_number) for current_file in preblob_names]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task            

# Say goodbye
print('\033[1;34;40mSubroutine "21" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')