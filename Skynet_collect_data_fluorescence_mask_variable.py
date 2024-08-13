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
import pandas as pd
import skimage as ski

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "20": Quantify fluoresence intensity in masks of your choice (with skimage). \033[1;37;40m \n')

# Location of mask images to process
print('')
mask_input_path = input('\033[2;37;40mPlease provide the location of the mask files (cell, nucleus and cytoplasm) from which to assemble the data: \033[1;37;40m \n')
# Location of csv files to process
print('')
image_input_path = input('\033[2;37;40mPlease provide the location of the image files from which you want to acquire intensity measurements: \033[1;37;40m \n')
# Location of the MIP files
print('')
output_path = input('\033[2;37;40mPlease provide the location which the assembled data should be exported: \033[1;37;40m \n')
# specificy how many objects to quantify
print('')
object_input_number = int(input('\033[2;37;40mPlease state the number of objects to be quantified: \033[1;37;40m \n'))
# make list of strings for objects
object_list = []
for current_object in range(object_input_number):
    print('For object:', str(current_object + 1))
    object_name = input('\033[2;37;40mState the _exact_ name of object as indicated by the masks file\033[1;37;40m \n')
    object_list.append(object_name)
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
def make_and_save_quantification(mask_input_path, image_input_path, output_path, current_index, object_mask_names, image_names, current_object):
    
       
    # experimental body
    current_object_mask_name = object_mask_names[current_index]
    #current_nucleus_mask_name = nucleus_mask_names[current_index]
    current_prefix = current_object_mask_name[0:len(current_object_mask_name)-24-len(current_object)]
    
    current_image_names = [x for x in image_names if re.search(current_prefix, x)]; 
    
    current_object_mask = cv2.imread('/'.join([mask_input_path,current_object_mask_name]), cv2.IMREAD_UNCHANGED)
    #current_nucleus_mask = cv2.imread('/'.join([mask_input_path,current_nucleus_mask_name]), cv2.IMREAD_UNCHANGED)
    y_pixel, x_pixel = np.shape(current_object_mask)
    
    current_images = np.ndarray(shape=(y_pixel,x_pixel,channel_input_number), dtype=np.uint16);
    
    for current_channel in range(channel_input_number):
        current_name_image = current_image_names[current_channel]
        current_channel_image = cv2.imread('/'.join([image_input_path,current_name_image]), cv2.IMREAD_UNCHANGED)
        current_channel_image[current_channel_image < int(background_list[current_channel])] = int(background_list[current_channel])
        background_substracted = current_channel_image - int(background_list[current_channel])
        current_images[:,:,current_channel] = background_substracted

    # do quantification here
    # new
    list_properties = ['label','area','area_bbox','axis_major_length','axis_minor_length','centroid','eccentricity','equivalent_diameter_area','perimeter','solidity',
                       'euler_number','extent','intensity_max','intensity_min','intensity_std','intensity_mean']
    cell_properties = ski.measure.regionprops_table(current_object_mask,current_images, properties = list_properties)
    pd_cell_data = pd.DataFrame(cell_properties)
    # calculate sum intensity
    cell_area = pd_cell_data.area.to_numpy()
    # intensity columns
    filtered_pd_cell_data = pd_cell_data.filter(like = 'intensity_mean')
    intensity_cell_data = filtered_pd_cell_data.to_numpy()
    num_channel = np.shape(filtered_pd_cell_data)[1]
    integrated_intensity_array = np.zeros(np.shape(filtered_pd_cell_data),dtype=float)
    for current_channel in range(num_channel):
        integrated_intensity_array[:,current_channel] = intensity_cell_data[:,current_channel]*cell_area
        pd_cell_data.insert(np.shape(pd_cell_data)[1],''.join(['intensity_integrated-',str(current_channel)]),integrated_intensity_array[:,current_channel])
    
    # add object name to each column 
    num_columns = np.shape(pd_cell_data)[1]
    for current_column in range(num_columns):
        current_name = pd_cell_data.columns[current_column]
        new_name = ''.join([current_name,'_',current_object])
        pd_cell_data.rename(columns={current_name: new_name},inplace=True)
                
        
    pandas_quantification_storage = pd_cell_data
    prefix = current_object_mask_name[0:len(current_object_mask_name)-5-len(current_object)]
    data_name = ''.join([prefix,'_',current_object,'_quantification.csv'])
    save_name = '/'.join([output_path,data_name])
    pandas_quantification_storage.to_csv(save_name, index = False, header = True)

# end monster function

mask_names = [current_file for current_file in listdir(mask_input_path) if isfile('/'.join([mask_input_path, current_file]))]

print('\033[1;34;40mWe now will extract data from',str(object_input_number),'objects. \033[1;37;40m \n') 

with alive_bar(object_input_number) as bar:
    for current_object in object_list:

        object_mask_names = [x for x in mask_names if re.search(''.join(['_',current_object]), x)];
        # nucleus_mask_names = [x for x in mask_names if re.search('_nucleus', x)];
        image_names = [current_file for current_file in listdir(image_input_path) if isfile('/'.join([image_input_path, current_file]))]
        
        number_files = len(object_mask_names)
        
        print('\033[1;34;40mWe identified',str(number_files),'mask images to use for data extraction. \033[1;37;40m \n') 

        
        with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
            # Submit all tasks to the executor at once
            Futures = [executor.submit(make_and_save_quantification, mask_input_path, image_input_path, output_path, current_index, object_mask_names, image_names, current_object) for current_index in range(number_files)]
                
            
                    
        bar()
# Say goodbye
print('\033[1;34;40mSubroutine "20" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')