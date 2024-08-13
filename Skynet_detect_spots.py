# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 19:10:32 2024

@author: b.kramer
"""

import os
import bigfish
import bigfish.stack as stack
import bigfish.detection as detection
#import bigfish.plot as plot
import sys
from os import listdir
from os.path import isfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np
#from alive_progress import alive_bar
import pandas as pd
import re
from alive_progress import alive_bar
import concurrent.futures
from PIL import Image as im
print("Big-FISH version: {0}".format(bigfish.__version__))

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "11": Detect and save counts of FISH-spots in images. \033[1;37;40m \n')

# Inputs
# Location where input images are location
print('')
input_path = input('\033[2;37;40mPlease provide the location where the images are location from which spots counts should be extracted: \033[1;37;40m \n')
# Location where output should be saved
print('')
output_path = input('\033[2;37;40mPlease provide the location where the results should be saved: \033[1;37;40m \n')
# In which channel do you want to determine spot counts
print('')
spots_channel = int(input('\033[2;37;40mFrom which channel do you want to extract spot counts (1,2.... N): \033[1;37;40m \n'))
# Set Threshold Estimation Mode
print('')
threshold_mode = input('\033[2;37;40mHow is the threshold for spot detection determined ("Auto" or a set integer): \033[1;37;40m \n')
if not threshold_mode == 'Auto':
    threshold_mode = float(threshold_mode)
# Set pixel_size
print('')
pixel_size = float(input('\033[2;37;40mWhat is the pixel size (1d, in nm): \033[1;37;40m \n'))
# Guess object radius
print('')
object_radius = float(input('\033[2;37;40mWhat suspected radius of the spots (in nm): \033[1;37;40m \n'))
# Radius of Segmentation
print('')
segmentation_radius = int(input('\033[2;37;40mHow large do you wish the segmentation radius for visualization to be (1,2...N): \033[1;37;40m \n'))
# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mFinally, how big is your tool (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
print('')
if number_worker == 'MusclePower':  
    print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
else:
   print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n')
     
# Make Strings for subfolders


output_path_data = '/'.join([output_path, 'QUANTIFICATION'])
output_path_segmentation = '/'.join([output_path, 'SEGMENTATION'])
output_path_spot_images = '/'.join([output_path, 'SPOTIMAGES'])

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

# Create Quantifaction folder if not already existing
if not os.path.exists(output_path_data):
        os.mkdir(output_path_data)

# Create PNG folder if not already existing
if not os.path.exists(output_path_segmentation):
        os.mkdir(output_path_segmentation)

# Create PNG folder if not already existing
if not os.path.exists(output_path_spot_images):
        os.mkdir(output_path_spot_images)
# End of path cheks


# Define Function
def quantify_spot_count(output_path_data, current_file, pixel_size, object_radius, segmentation_radius):
    
    # Get prefix
    prefix = current_file[0:len(current_file)-4]
    
    # Read current image
    current_image = stack.read_image('/'.join([input_path,current_file]))
    
    # Determine spot parameters
    # spot radius
    spot_radius_px = detection.get_object_radius_pixel(
        voxel_size_nm=(pixel_size, pixel_size), 
        object_radius_nm=(object_radius, object_radius), 
        ndim=2)

    # Apply LoG Filter
    filtered_image = stack.log_filter(current_image,spot_radius_px)
    
    # Detect local maxima
    mask = detection.local_maximum_detection(filtered_image, min_distance=spot_radius_px)
    
    if threshold_mode == 'Auto':
        # Do an automated thresholding
        Threshold = detection.automated_threshold_setting(filtered_image, mask)
    else:
        Threshold = threshold_mode
    
    # Detect spots
    spots, _ = detection.spots_thresholding(filtered_image, mask, Threshold)
    
    # Decompose dense regions
    decomposed_spots, dense_regions, reference_spot = detection.decompose_dense(
    image=current_image, 
    spots=spots, 
    voxel_size=(pixel_size, pixel_size), 
    spot_radius=(object_radius, object_radius), 
    alpha=0.7,  # alpha impacts the number of spots per candidate region
    beta=1,  # beta impacts the number of candidate regions to decompose
    gamma=5)  # gamma the filtering step to denoise the image
        
    # Transform to dataframe     
    spot_pandas = pd.DataFrame(spots)
    decomposed_spot_pandas = pd.DataFrame(decomposed_spots)
    
    # save the dataframe
    save_name_spots = ''.join([output_path_data,'/',prefix,'_spots_Positions.csv'])
    spot_pandas.to_csv(save_name_spots, index = False, header = False)
    save_name_decomposed = ''.join([output_path_data,'/',prefix,'_decomposed_spots_Positions.csv'])
    decomposed_spot_pandas.to_csv(save_name_decomposed, index = False, header = False)
    
    # Provide a convenient sum
    sum_spots = len(spots)
    sum_decomposed_spots = len(decomposed_spots)
    
    # Transform to dataframe
    sum_spots_pandas = pd.DataFrame([sum_spots],[0])
    sum_decomposed_spots_pandas = pd.DataFrame([sum_decomposed_spots],[0])
    
    # save the dataframe
    save_name_sum_spots = ''.join([output_path_data,'/',prefix,'_spots_Sum.csv'])
    sum_spots_pandas.to_csv(save_name_sum_spots, index = False, header = False)
    save_name_sum_decomposed = ''.join([output_path_data,'/',prefix,'_decomposed_spots_Sum.csv'])
    sum_decomposed_spots_pandas.to_csv(save_name_sum_decomposed, index = False, header = False)
    
    # Save Spot Images
    save_spot_image(current_image, spots, decomposed_spots, prefix)   
    # Save Segmentation Images (Polygon hack)
    distance = segmentation_radius 
    make_segmentation_image(current_image, spots, prefix, distance)
    
def save_spot_image(current_image, spots, decomposed_spots, prefix):
    
    # Normal spots
    spot_image = np.zeros_like(current_image)
    for y_coord, x_coord in spots[:, :2]:
        spot_image[y_coord, x_coord] = spot_image[y_coord, x_coord] + 1
    
    spot_image = im.fromarray(spot_image)
    spot_save_name = ''.join([output_path_spot_images,'/',prefix,'_spots.png'])
    spot_image.save(spot_save_name)
    
    # Decomposed
    decomposed_image = np.zeros_like(current_image)
    for y_coord, x_coord in decomposed_spots[:, :2]:
        decomposed_image[y_coord, x_coord] =  decomposed_image[y_coord, x_coord] + 1
    
    decomposed_image = im.fromarray(decomposed_image)
    decomposed_save_name = ''.join([output_path_spot_images,'/',prefix,'_decomposed_spots.png'])
    decomposed_image.save(decomposed_save_name)

def make_segmentation_image(current_image, spots, prefix, distance):
    segmentation_image = np.zeros_like(current_image)
    y_dimension_image, x_dimension_image = segmentation_image.shape[:2]

    for y_coord, x_coord in spots:
        y_range = np.clip(np.arange(y_coord - distance, y_coord + distance + 1), 0, y_dimension_image - 1)
        XRange = np.clip(np.arange(x_coord - distance, x_coord + distance + 1), 0, x_dimension_image - 1)

        YPoints, XPoints = np.meshgrid(y_range, XRange)
        Manhattandistance = np.abs(YPoints - y_coord) + np.abs(XPoints - x_coord)

        segmentation_image[YPoints[Manhattandistance == distance], XPoints[Manhattandistance == distance]] = 1

    segmentation_image = im.fromarray(segmentation_image)
    segmentation_save_name = ''.join([output_path_segmentation,'/',prefix,'_Segmentation.png'])
    segmentation_image.save(segmentation_save_name)    
    

# MainBody
image_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
  
# Get Images with that wavelenght
images_channel = [x for x in image_names if re.search(f'W0{spots_channel:03}', x)] 
number_images = len(images_channel)
print('\033[1;34;40mWe identified',str(number_images),'unique Image files with that channel index. \033[1;37;40m \n') 

#with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:    
    #for current_file in images_channel:
        #executor.submit(quantify_spot_count, output_path_data, current_file, pixel_size, object_radius)
 
with alive_bar(number_images) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(quantify_spot_count, output_path_data, current_file, pixel_size, object_radius, segmentation_radius) for current_file in images_channel]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task

# Say goodbye
print('\033[1;34;40mSubroutine "11" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')
