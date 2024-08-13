# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 19:10:32 2024

@author: b.kramer
"""

import os
import bigfish
import bigfish.stack as stack
import bigfish.detection as detection
import sys
import numpy as np
from os import listdir
from os.path import isfile
from concurrent.futures import ThreadPoolExecutor
from alive_progress import alive_bar
from PIL import Image as im
import matplotlib
# Turn off interactive plotting
matplotlib.use('Agg')
import bigfish.plot as plot
import concurrent.futures
import pandas as pd
import re
print("Big-FISH version: {0}".format(bigfish.__version__))



os.system('color')
 
# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "10": Estimate an appropriate threshold for FISH spot detection. \033[1;37;40m \n')

# Start of inputs
# Location above "NIS" folder
print('')
input_path = input('\033[2;37;40mPlease provide the location of the where the test images are located: \033[1;37;40m \n')
print('')
output_path = input('\033[2;37;40mPlease provide the location of the where results should be saved: \033[1;37;40m \n')
# get wavelength
print('')
spots_channel = int(input('\033[2;37;40mIn which channel should the spot detection be performed \033[1;37;40m \n'))
# Set pixel_size
print('')
pixel_size = float(input('\033[2;37;40mWhat is the pixel size (1d, in nm): \033[1;37;40m \n'))
# Guess object radius
print('')
object_radius = float(input('\033[2;37;40mWhat suspected radius of the spots (in nm): \033[1;37;40m \n'))
# Radius of Segmentation
print('')
segmentation_radius = int(input('\033[2;37;40mHow large do you wish the segmentation radius for visualization to be (1,2...N): \033[1;37;40m \n'))
# Side By Side
print('')
comparison_mode = input('\033[2;37;40mDo you wish to also save a side-by-side comparison with Spot segmentation overlay ("Yes","No")? \033[1;37;40m \n')
# Threshold range mode
print('')
threshold_range = input('\033[2;37;40mDo you wish the center of threshold estimation be determined automatically (will vary per image) or be provided value ("Auto","Manual"): \033[1;37;40m \n')
if threshold_range == 'Manual':
    print('')
    threshold_center = int(input('\033[2;37;40mWhich integer do you wish to be the center of threshold estimation (Recom: ~140):  \033[1;37;40m \n'))
# Threshold Increments
print('')
threshold_increments = int(input('\033[2;37;40mIn which step size do you want to assess thresholds from center (Recom: 5-10): \033[1;37;40m \n'))  
# Range of threshold stepping
print('')
threshold_step = int(input('\033[2;37;40mHow many steps do you want to explore thresholds in both directions (1,2....N): \033[1;37;40m \n'))      
# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mState how well is your machine endowed (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
print('')
if number_worker == 'MusclePower':  
    print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
else:
   print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n')
  
# Make necessary paths
output_path_final = '/'.join([output_path, 'THRESHOLDS'])
output_path_temp = '/'.join([output_path, 'TEMP'])
output_path_temp_images = '/'.join([output_path, 'TEMP','IMAGES'])
output_path_temp_spots = '/'.join([output_path, 'TEMP','spots'])

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

# Create final output folder if not already existing
if not os.path.exists(output_path_final):
        os.mkdir(output_path_final)

# Create temporary folder for if not already existing
if not os.path.exists(output_path_temp):
        os.mkdir(output_path_temp)

# Create temporary folder for images if not already existing
if not os.path.exists(output_path_temp_images):
        os.mkdir(output_path_temp_images)

# Create temporary folder for spot counts if not already existing
if not os.path.exists(output_path_temp_spots):
        os.mkdir(output_path_temp_spots)
# Define Function

def save_thresholds(output_path_final, output_path_temp_spots, prefix, current_image, filtered_image, pixel_size, object_radius, mask, current_threshold, segmentation_radius):
   
    # Detect spots
    spots, _ = detection.spots_thresholding(filtered_image, mask, current_threshold)
                 
    distance = segmentation_radius
    make_segmentation_image(output_path_final, current_image, spots, prefix, distance, current_threshold)
    save_spots_temp(output_path_temp_spots, spots, prefix, current_threshold)
 
def save_spots_temp(output_path_temp_spots, spots, prefix, current_threshold):
    
    spot_pandas = pd.DataFrame(spots)
    threshold_string = '\n'.join(['{0:03}'.format(int(current_threshold))])
    spot_save_name = ''.join([output_path_temp_spots,'/',prefix,'_','T',threshold_string,'.csv'])
    spot_pandas.to_csv(spot_save_name)
    

def make_segmentation_image(output_path_final, current_image, spots, prefix, distance, current_threshold):
    segmentation_image = np.zeros_like(current_image)
    y_dimension_image, x_dimension_image = segmentation_image.shape[:2]

    for y_coord, x_coord in spots:
        y_range = np.clip(np.arange(y_coord - distance, y_coord + distance + 1), 0, y_dimension_image - 1)
        x_range = np.clip(np.arange(x_coord - distance, x_coord + distance + 1), 0, x_dimension_image - 1)

        y_points, x_points = np.meshgrid(y_range, x_range)
        manhattan_distance = np.abs(y_points - y_coord) + np.abs(x_points - x_coord)

        segmentation_image[y_points[manhattan_distance == distance], x_points[manhattan_distance == distance]] = 1
        
    save_segmentation_image = im.fromarray(segmentation_image)
    threshold_string = '\n'.join(['{0:03}'.format(int(current_threshold))])
    segmentation_save_name = ''.join([output_path_final,'/','T',threshold_string,'_',prefix,'.png'])
    save_segmentation_image.save(segmentation_save_name)    
    
    # Plot side by side.. somehow
    #side_by_side_name = ''.join([output_path_final,'/','Comparison_T',ThresholdString,'_',prefix,'.png'])
    #sleep(25)
    #plot.plot_detection(current_image, Spots, contrast=True, path_output = side_by_side_name)
    #sleep(25)
    #matplotlib.pyplot.close()

def make_comparison_image(output_path_final, current_image, spots, prefix, t_suffix):

    side_by_side_name = ''.join([output_path_final,'/','Comparison_',t_suffix,'_',prefix,'.png'])  
    try:
        plot.plot_detection(current_image, spots, contrast=True, path_output = side_by_side_name)
        matplotlib.pyplot.close()
    except:
        print('ALL IS GOOD, but this one did not work')
        
def prepare_processing(input_path, output_path_final, output_path_temp_spots, current_file, pixel_size, object_radius, threshold_range, threshold_center, threshold_increments, segmentation_radius):
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
    
    # Do an automated thresholding
    if threshold_range == 'Auto':
        threshold_center = detection.automated_threshold_setting(filtered_image, mask)
    elif threshold_range == 'Manual': 
        threshold_center = threshold_center
    # Now loop over different thresholds in increments starting from the automatically identified one
    increment = threshold_increments
    threshold_list = [(threshold_center - i * increment) for i in range(threshold_step,0,-1)] + [(threshold_center + i * increment) for i in range(1, threshold_step+1)]
    for current_threshold in threshold_list:
        #executor.submit(save_thresholds, output_path_final, prefix, current_image, filtered_image, pixel_size, object_radius, mask, current_threshold, segmentation_radius)
        save_thresholds(output_path_final, output_path_temp_spots, prefix, current_image, filtered_image, pixel_size, object_radius, mask, current_threshold, segmentation_radius)  
       
def prepare_processing_minmal(input_path, current_file):
    
    # Get prefix
    prefix = current_file[0:len(current_file)-4]
    
    # Read current image
    current_image = stack.read_image('/'.join([input_path,current_file]))
    
    return prefix, current_image
              
# End of defining functions

# Main body
# Detect number of images in Subset
image_names_raw = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
# temp fix
image_names = [x for x in image_names_raw if re.search(f'W0{spots_channel:03}', x)] 
print('\033[1;34;40mWe identified',str(len(image_names)),'unique Image files. \033[1;37;40m \n')

    
with alive_bar(len(image_names)) as bar:
    with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(prepare_processing, input_path, output_path_final, output_path_temp_spots, current_file, pixel_size, object_radius, threshold_range, threshold_center, threshold_increments, segmentation_radius) for current_file in image_names]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task        

# Now do separate looping for bloody comparison image....
if comparison_mode == 'Yes':
    csv_names = [current_file for current_file in listdir(output_path_temp_spots) if isfile('/'.join([output_path_temp_spots, current_file]))]
    with alive_bar(len(image_names)) as bar:
        for current_file in image_names:
            prefix, current_image = prepare_processing_minmal(input_path, current_file)
            prefix = prefix[len(prefix)-20:len(prefix)]
            # get all csv with the prefix
            SpotCountFiles = [x for x in csv_names if re.search(prefix, x)]
            for CurrentSpotCountFile in SpotCountFiles:
                FullSuffix = CurrentSpotCountFile[len(CurrentSpotCountFile) - 8:]
                t_suffix = FullSuffix[0:len(FullSuffix)-4]
                SpotCount = pd.read_csv('/'.join([output_path_temp_spots,CurrentSpotCountFile]))
                spots = SpotCount.iloc[:,1:3].values
                make_comparison_image(output_path_final, current_image, spots, prefix, t_suffix)
            bar()
        
# Say goodbye
print('\033[1;34;40mSubroutine "10" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')
