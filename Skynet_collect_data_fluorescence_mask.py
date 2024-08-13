# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:37:33 2024

@author: b.kramer
"""

import numpy as np
from os import listdir
from os.path import isfile
import os
from concurrent.futures import ThreadPoolExecutor
from alive_progress import alive_bar
#import numpy as np
import re
import cv2
import concurrent.futures
import pandas as pd

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "15": Make quantification using big-fish spot counts and cell mask images (covering blobs). \033[1;37;40m \n')

# Location of mask images to process
print('')
mask_input_path = input('\033[2;37;40mPlease provide the location of the mask files (cell and nucleus) from which to assemble the data: \033[1;37;40m \n')
# Location of csv files to process
print('')
image_input_path = input('\033[2;37;40mPlease provide the location of the image files from which you want to acquire intensity measurements: \033[1;37;40m \n')
# Location of the MIP files
print('')
output_path = input('\033[2;37;40mPlease provide the location which the assembled data should be exported: \033[1;37;40m \n')
# number channels
print('')
channel_input_number = int(input('\033[2;37;40mFrom how many channels do you want to extract data [1,2...N] (Currently restricted to from 1 to N, and cannnot choose only what you need): \033[1;37;40m \n'))
# background per channel
background_list = []
for current_channel in range(channel_input_number):
    print('')
    channel_background = input('\033[2;37;40mIn order, choose the background (int) for the channels: \033[1;37;40m \n')
    background_list.append(channel_background)

# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mHow many proteins did you pack into your device (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
print('')
if number_worker == 'MusclePower':  
    print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
else:
   print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n')
# End of inputs  


# define monster function
def make_and_save_quantification(mask_input_path, image_input_path, output_path, current_index, cell_mask_names, image_names):
    
    # experimental body
    current_cell_mask_name = cell_mask_names[current_index]
    #current_nucleus_mask_name = nucleus_mask_names[current_index]
    current_prefix = current_cell_mask_name[0:len(current_cell_mask_name)-29]
    
    current_image_names = [x for x in image_names if re.search(current_prefix, x)]; 
    
    current_cell_mask = cv2.imread('/'.join([mask_input_path,current_cell_mask_name]), cv2.IMREAD_UNCHANGED)
    #current_nucleus_mask = cv2.imread('/'.join([mask_input_path,current_nucleus_mask_name]), cv2.IMREAD_UNCHANGED)
    y_pixel, x_pixel = np.shape(current_cell_mask)
    
    current_images = np.ndarray(shape=(y_pixel,x_pixel,channel_input_number), dtype=np.uint16);
    
    for current_channel in range(channel_input_number):
        current_name_image = current_image_names[current_channel]
        current_channel_image = cv2.imread('/'.join([image_input_path,current_name_image]), cv2.IMREAD_UNCHANGED)
        current_channel_image[current_channel_image < int(background_list[current_channel])] = int(background_list[current_channel])
        background_substracted = current_channel_image - int(background_list[current_channel])
        current_images[:,:,current_channel] = background_substracted

    # now do quantifications in label images
    unique_labels = np.unique(current_cell_mask)
    # delete 0 label
    unique_labels = np.delete(unique_labels, 0, 0)
    boolean_cell_mask_image = np.copy(current_cell_mask)
    boolean_cell_mask_image[boolean_cell_mask_image > 1] = 1
    
    #boolean_nucleus_mask_image = np.copy(current_nucleus_mask)
    #boolean_nucleus_mask_image[boolean_nucleus_mask_image > 1] = 1

    quantification_storage = np.zeros((len(unique_labels),(channel_input_number*2)+1),dtype = np.float64)

    for current_cell in range(len(unique_labels)):
        current_label = unique_labels[current_cell]
        #current_nucleus_area = np.sum(boolean_nucleus_mask_image[current_nucleus_mask == current_label])        
        current_cell_area = np.sum(boolean_cell_mask_image[current_cell_mask == current_label])
        #quantification_storage[current_cell,0] = current_nucleus_area
        quantification_storage[current_cell,0] = current_cell_area
        
        insert_index = 1
        for current_channel in range(channel_input_number):
            current_quantification_image = current_images[:,:,current_channel]
            
            #integrated_nucleus_intensity = np.sum(current_quantification_image[current_nucleus_mask == current_label])
            #mean_nucleus_intensity = integrated_nucleus_intensity/current_nucleus_area
            integrated_cell_intensity = np.sum(current_quantification_image[current_cell_mask == current_label])
            mean_cell_intensity = integrated_cell_intensity/current_cell_area
            
            
            #quantification_storage[current_cell,insert_index] = integrated_nucleus_intensity
            #insert_index = insert_index + 1
            #quantification_storage[current_cell,insert_index] = mean_nucleus_intensity
            #insert_index = insert_index + 1
            quantification_storage[current_cell,insert_index] = integrated_cell_intensity
            insert_index = insert_index + 1
            quantification_storage[current_cell,insert_index] = mean_cell_intensity
            insert_index = insert_index + 1
       
    column_names = []
    #column_names.append('ncuelus_area')
    column_names.append('cell_area')
    
    for current_channel in range(channel_input_number):
        channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
        #column_names.append(''.join(['integrated_nucleus_intensity_',channel_string]))
        #column_names.append(''.join(['mean_nucleus_intensity_',channel_string]))
        column_names.append(''.join(['integrated_cell_intensity_',channel_string]))
        column_names.append(''.join(['mean_cell_intensity_',channel_string]))
        
    pandas_quantification_storage = pd.DataFrame(quantification_storage,columns = column_names)
    prefix = current_cell_mask_name[0:len(current_cell_mask_name)-9]
    data_name = ''.join([prefix,'_quantification.csv'])
    save_name = '/'.join([output_path,data_name])
    pandas_quantification_storage.to_csv(save_name, index = False, header = True)

# end monster function

# main body
mask_names = [current_file for current_file in listdir(mask_input_path) if isfile('/'.join([mask_input_path, current_file]))]
cell_mask_names = [x for x in mask_names if re.search('_cell', x)];
# nucleus_mask_names = [x for x in mask_names if re.search('_nucleus', x)];

image_names = [current_file for current_file in listdir(image_input_path) if isfile('/'.join([image_input_path, current_file]))]


number_files = len(cell_mask_names)

print('\033[1;34;40mWe identified',str(number_files),'mask images to use for data extraction. \033[1;37;40m \n') 

with alive_bar(number_files) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(make_and_save_quantification, mask_input_path, image_input_path, output_path, current_index, cell_mask_names, image_names) for current_index in range(number_files)]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task

# Say goodbye
print('\033[1;34;40mSubroutine "15" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')