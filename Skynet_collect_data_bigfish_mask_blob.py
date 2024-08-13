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
print('\033[1;34;40mYou accessed subroutine "16": Make quantification using big-fish spot counts and cell mask images (covering blobs). \033[1;37;40m \n')

# Location of mask images to process
print('')
input_path = input('\033[2;37;40mPlease provide the location of the mask files (cell, blob and spot_images/decomposed_spot_images) from which to assemble the data: \033[1;37;40m \n')
# Location of csv files to process
print('')
csv_input_path = input('\033[2;37;40mPlease provide the location of csv files containing spot locations (spot and decomposed): \033[1;37;40m \n')
# Location of the MIP files
print('')
output_path = input('\033[2;37;40mPlease provide the location which the assembled data should be exported: \033[1;37;40m \n')
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
def make_and_save_quantification(input_path, output_path, current_index, cell_mask_names, blob_mask_names, spot_csv_names, decomposed_spot_csv_names):
    
    # experimental body
    current_cell_mask_name = cell_mask_names[current_index]
    current_blob_mask_name = blob_mask_names[current_index]

    current_spot_csv_name = spot_csv_names[current_index]
    current_decomposed_spot_csv_name = decomposed_spot_csv_names[current_index]
        
    current_cell_mask = cv2.imread('/'.join([input_path,current_cell_mask_name]), cv2.IMREAD_UNCHANGED)
    current_blob_mask = cv2.imread('/'.join([input_path,current_blob_mask_name]), cv2.IMREAD_UNCHANGED)

    current_spot_pandas = pd.read_csv('/'.join([csv_input_path,current_spot_csv_name]))
    current_decomposed_spot_pandas = pd.read_csv('/'.join([csv_input_path,current_decomposed_spot_csv_name]))

    array_spot_positions = current_spot_pandas.to_numpy()
    array_decomposed_spot_positions = current_decomposed_spot_pandas.to_numpy()

    # turn spot positions into image
    spot_image = np.zeros((np.shape(current_cell_mask)[0], np.shape(current_cell_mask)[1]),dtype=np.uint16)
    decomposed_spot_image = np.zeros((np.shape(current_cell_mask)[0], np.shape(current_cell_mask)[1]),dtype=np.uint16)

    #np add at
    np.add.at(spot_image, (array_spot_positions[:, 0], array_spot_positions[:, 1]), 1)
    np.add.at(decomposed_spot_image,(array_decomposed_spot_positions[:, 0], array_decomposed_spot_positions[:, 1]), 1)

    # make covered images
    boolean_blob_mask = np.copy(current_blob_mask)
    boolean_blob_mask[boolean_blob_mask > 0] = 1

    covered_spot_image = np.copy(spot_image)
    covered_decomposed_spot_image = np.copy(decomposed_spot_image)

    covered_spot_image[boolean_blob_mask > 0] = 0
    covered_decomposed_spot_image[boolean_blob_mask > 0] = 0

    # now do quantifications in label images
    unique_labels = np.unique(current_cell_mask)
    # delete 0 label
    unique_labels = np.delete(unique_labels, 0, 0)

    quantification_storage = np.zeros((len(unique_labels),4),dtype = np.float64)

    for current_cell in range(len(unique_labels)):
        current_label = unique_labels[current_cell]
        current_spots = np.sum(spot_image[current_cell_mask == current_label])
        current_decomposed_spots = np.sum(decomposed_spot_image[current_cell_mask == current_label])
        current_covered_spots = np.sum(covered_spot_image[current_cell_mask == current_label])
        current_covered_decomposed_spots = np.sum(covered_decomposed_spot_image[current_cell_mask == current_label])
        quantification_storage[current_cell,0] = current_spots
        quantification_storage[current_cell,1] = current_covered_spots
        quantification_storage[current_cell,2] = current_decomposed_spots
        quantification_storage[current_cell,3] = current_covered_decomposed_spots

    int_quantification_storage = quantification_storage.astype(int)
    column_names = ['spots','spots_no_blob','decomposed_spots','decomposed_spots_no_blob']
    pandas_quantification_storage = pd.DataFrame(int_quantification_storage,columns = column_names)
    prefix = current_cell_mask_name[0:len(current_cell_mask_name)-9]
    data_name = ''.join([prefix,'_quantification.csv'])
    save_name = '/'.join([output_path,data_name])
    pandas_quantification_storage.to_csv(save_name, index = False, header = True)

# end monster function

# main body
mask_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
cell_mask_names = [x for x in mask_names if re.search('_cell', x)];
blob_mask_names = [x for x in mask_names if re.search('_blob', x)];

csv_names = [current_file for current_file in listdir(csv_input_path) if isfile('/'.join([csv_input_path, current_file]))]
spot_csv_names = [x for x in csv_names if re.search('1_spots_Positions', x)];
decomposed_spot_csv_names = [x for x in csv_names if re.search('1_decomposed_spots_Positions', x)];

number_files = len(cell_mask_names)

with alive_bar(number_files) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(make_and_save_quantification, input_path, output_path, current_index, cell_mask_names, blob_mask_names, spot_csv_names, decomposed_spot_csv_names) for current_index in range(number_files)]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task

# Say goodbye
print('\033[1;34;40mSubroutine "16" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')