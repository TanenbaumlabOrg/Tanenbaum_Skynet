# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""

import numpy as np
from PIL import Image as im
from os import listdir
from os.path import isfile
import os
from concurrent.futures import ThreadPoolExecutor
import sys
from alive_progress import alive_bar
#import numpy as np
import re
import cv2
import concurrent.futures


os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "14": Relabel nucleus to the same label as cells and make the masks consistent. \033[1;37;40m \n')

# Start of inputs
# Location of nuclei masks
print('')
input_path_nucleus = input('\033[2;37;40mPlease provide the location of the nuclei masks: \033[1;37;40m \n')
# Location of cell masks
print('')
input_path_cell = input('\033[2;37;40mPlease provide the location of the cell masks: \033[1;37;40m \n')
# Location of the MIP files
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish consistent label images to be saved: \033[1;37;40m \n')
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
if not os.path.exists(input_path_nucleus):
    print('')
    print('\033[1;31;40mYou are a moron. The path to nuclei masks does not exist. \033[1;37;40m \n')
    print('\033[1;31;40mTry again with the correct path. \033[1;37;40m \n')
    sys.exit()
elif len(os.listdir(input_path_nucleus)) == 0:    
    print('')
    print('\033[1;31;40mYou are an even bigger moron. There are no files in that directory. \033[1;37;40m \n')
    print('\033[1;31;40mTry putting it in first. \033[1;37;40m \n')

# Check path information (consistency)
if not os.path.exists(input_path_cell):
    print('')
    print('\033[1;31;40mYou are a moron. The path to cell masks does not exist. \033[1;37;40m \n')
    print('\033[1;31;40mTry again with the correct path. \033[1;37;40m \n')
    sys.exit()
elif len(os.listdir(input_path_cell)) == 0:    
    print('')
    print('\033[1;31;40mYou are an even bigger moron. There are no files in that directory. \033[1;37;40m \n')
    print('\033[1;31;40mTry putting it in first. \033[1;37;40m \n')
else:
    print('')
    print('\033[1;33;40mFor now, we will acknowledge your supremacy and are processing your request. Standby. \033[1;37;40m \n')    

# Create MIP folder if not already existing
if not os.path.exists(output_path):
        os.mkdir(output_path)
# end of path information

def save_images(current_nucleus_image, current_cell_image, current_cytoplasm_image, prefix , output_path):
    
    image_nucleus_png = im.fromarray(current_nucleus_image)
    image_cell_png = im.fromarray(current_cell_image)
    image_cytoplasm_png = im.fromarray(current_cytoplasm_image)
    nucleus_name = ''.join([prefix,'_nucleus.png'])
    cell_name = ''.join([prefix,'_cell.png'])
    cytoplasm_name = ''.join([prefix,'_cytoplasm.png'])
    
    save_name_nucleus = '/'.join([output_path,nucleus_name])
    save_name_cell = '/'.join([output_path,cell_name])
    save_name_cytoplasm = '/'.join([output_path,cytoplasm_name])
    
    image_nucleus_png.save(save_name_nucleus)
    image_cell_png.save(save_name_cell)
    image_cytoplasm_png.save(save_name_cytoplasm)

     
def make_covered_image(current_index, input_path_nucleus, input_path_cell, output_path):
    
    current_nucleus_file = nucleus_images[current_index]
    current_cell_file = cell_images[current_index]
    prefix = current_nucleus_file[0:len(current_nucleus_file)-12]
    current_nucleus_image = cv2.imread('/'.join([input_path_nucleus,current_nucleus_file]), cv2.IMREAD_UNCHANGED)
    current_cell_image = cv2.imread('/'.join([input_path_cell,current_cell_file]), cv2.IMREAD_UNCHANGED)
    
    transformed_cell_image = current_cell_image.copy()
    transformed_nucleus_image = current_nucleus_image.copy()
    
    # get unique labels nucleus
    unique_nucleus = np.unique(current_nucleus_image)
                                
    # delete first entry
    unique_nucleus = unique_nucleus[1:len(unique_nucleus):1]
    # now make consistent labeling
    for current_label in unique_nucleus:
        index_nucleus = np.where(current_nucleus_image == current_label)
        label_in_cell = current_cell_image[index_nucleus]
        most_frequent_label = np.bincount(label_in_cell).argmax()
        most_frequent_label = most_frequent_label.astype(np.uint16)
        transformed_nucleus_image[index_nucleus] = most_frequent_label
    
    transformed_nucleus_image[transformed_cell_image == 0] = 0
    transformed_cell_image[transformed_nucleus_image > 0] = 0
    
    final_cell_image = transformed_cell_image + transformed_nucleus_image
     
    current_cell_image = final_cell_image
    current_cytoplasm_image = transformed_cell_image
    current_nucleus_image = transformed_nucleus_image
    
    # another round of uniques
    final_unique_nucleus = np.unique(current_nucleus_image)
    final_unique_cell = np.unique(current_cell_image)
    difference_label = np.setdiff1d(final_unique_cell,final_unique_nucleus)
    
    for current_label in difference_label:
        current_cell_image[current_cell_image == current_label] = 0
        current_cytoplasm_image[current_cytoplasm_image == current_label] = 0
        
    
    save_images(current_nucleus_image, current_cell_image, current_cytoplasm_image, prefix, output_path)


# main body
# find all images
nucleus_all_images = [current_file for current_file in listdir(input_path_nucleus) if isfile('/'.join([input_path_nucleus, current_file]))]
cell_all_images = [current_file for current_file in listdir(input_path_cell) if isfile('/'.join([input_path_cell, current_file]))]

# only extract with nucleus and cell 
nucleus_images = [x for x in nucleus_all_images if re.search('_nucleus', x)];
cell_images = [x for x in cell_all_images if re.search('_cell', x)];
number_images = len(cell_images)

print('\033[1;34;40mWe identified',str(number_images),'images to subject to covering. \033[1;37;40m \n')

with alive_bar(number_images) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(make_covered_image, current_index, input_path_nucleus, input_path_cell, output_path) for current_index in range(0,number_images)]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task

# Say goodbye
print('\033[1;34;40mSubroutine "14" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')

