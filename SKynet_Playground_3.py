# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
import nd2
from PIL import Image as im
from os import listdir
from os.path import isfile
import os
from concurrent.futures import ThreadPoolExecutor
import sys
from alive_progress import alive_bar
import numpy as np

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "2": Export .png from .nd2 files. \033[1;37;40m \n')

# Start of inputs
# Location of .nd2 files
print('')
input_path = input('\033[2;37;40mPlease provide the location of the .nd2 files: \033[1;37;40m \n')
# Location of the metadata
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish .png files to be exported: \033[1;37;40m \n')
# Chunks size for parralel loading
print('')
chunk_size = int(input('\033[2;37;40mState the chunk size which can be loaded in one batch [1,2,...N]: \033[1;37;40m \n'))
# Add additional Prefix
#print('')
#prefix_indicator = input('\033[2;37;40mDo you wish to have an additional prefix/indicator added to the .pngs based on their position number ("Yes"/"No")? \033[1;37;40m \n')
#if prefix_indicator == 'Yes':
    #print('')
    #chunk_number = int(input('\033[2;37;40mInto how many separate chunks should the data be separated [1,2,.....N]? \033[1;37;40m \n'))
    #prefix_list = []
    #for current_chunk in range(chunk_number):
        #print('')
        #current_prefix = input('\033[2;37;40mChoose the prefix for chunk: \033[1;37;40m \n')
        #prefix_list.append(current_prefix)
# How many workers will be used for parallelization
print('')
number_worker = input('\033[2;37;40mWhat is the size of your tool today (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]?): \033[1;37;40m \n')
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

# Create metadata folder if not already existing
if not os.path.exists(output_path):
        os.mkdir(output_path)
# End of path information 

# Start defining functions
#def process_z_position_nd2(output_path, prefix, dask_image_stack, current_xy, current_z, channels, time_points, time, chunk_prefix, prefix_take, sub_chunks):
    #z_string = '\n'.join(['{0:04}'.format(current_z + 1)])
    #if prefix_indicator == 'Yes':
        #xy_string = '\n'.join(['{0:04}'.format((current_xy + 1)-(prefix_take*sub_chunks))])
    #else:
        #xy_string = '\n'.join(['{0:04}'.format(current_xy + 1)])
    #for current_channel in range(channels):
        #channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
        #for current_t in range(time_points) if time else [0]:
            #sub_image_stack = np.asarray(dask_image_stack[current_t, current_xy, current_z, current_channel, :, :]) if time else np.asarray(dask_image_stack[current_xy, current_z, current_channel, :, :])
            #time_string = '\n'.join(['{0:04}'.format(current_t + 1)])
            # ImagePNG = im.fromarray(CurrentImageStack[CurrentT, CurrentXY, CurrentZ, CurrentChannel, :, :]) if Time else im.fromarray(CurrentImageStack[CurrentXY, CurrentZ, CurrentChannel, :, :])
            #image_png = im.fromarray(sub_image_stack[:, :]) if time else im.fromarray(sub_image_stack[:, :])
            #save_name_image = ''.join([chunk_prefix,prefix, '_', 'P', xy_string, 'T', time_string, 'W', channel_string, 'Z', z_string, '.png'])
            #save_name_full = '/'.join([output_path, save_name_image])
            #image_png.save(save_name_full)
# End of defining functions

def process_chunk(output_path, prefix, dask_chunk_storage, current_list, current_entry):
    current_combination = current_list[current_entry]
    current_t, current_xy, current_z, current_channel = current_combination
    sub_image_stack = dask_chunk_storage[current_entry,:,:]
    z_string = '\n'.join(['{0:04}'.format(current_z + 1)])
    xy_string = '\n'.join(['{0:04}'.format(current_xy + 1)])
    time_string = '\n'.join(['{0:04}'.format(current_t + 1)])
    channel_string = '\n'.join(['{0:04}'.format(current_channel + 1)])
    image_png = im.fromarray(sub_image_stack[:, :]) 
    save_name_image = ''.join([prefix, '_', 'P', xy_string, 'T', time_string, 'W', channel_string, 'Z', z_string, '.png'])
    save_name_full = '/'.join([output_path, save_name_image])
    image_png.save(save_name_full)
    
# Main body
nd2_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
print('\033[1;34;40mWe identified',str(len(nd2_names)),'unique NIS files. \033[1;37;40m \n')

with alive_bar(len(nd2_names)) as bar: 
    for current_file in nd2_names:       
        dask_image_stack = nd2.imread('/'.join([input_path, current_file]), dask = True)  
        nd2_file = nd2.ND2File('/'.join([input_path, current_file]))  
        nd2_sizes = nd2_file.sizes
        
        # Initialize variables directly from nd2_sizes or default to 1, and set truth flags accordingly
        keys = ['T', 'P', 'Z', 'C', 'Y', 'X']
        results = {key: [nd2_sizes.get(key, 1), 0] for key in keys}
        nd2_file.close()
        for key in keys:
            if key in nd2_sizes:
                results[key][1] = 1
            else:
                # If the key is not in nd2_sizes, it means the value was defaulted to 1
                results[key][0] = 1
                results[key][1] = 0

        # Unpack the values into variables
            time_points, time_true = results['T']
            xy_positions, xy_true = results['P']
            z_positions, z_true = results['Z']
            channels, channel_true = results['C']
            y_pixel_number, y_pixel_true = results['Y']
            x_pixel_number, x_pixel_true = results['X']
      
        prefix = current_file[0:len(current_file) - 4]

        #if prefix_indicator == 'Yes':
            #prefix_take = 0
            #sub_chunks = int(xy_positions/chunk_number)
        #else:
            #chunk_prefix = []
            #prefix_take = 0
            #sub_chunks = 0
            
        time_vector = np.arange(time_points)
        xy_vector = np.arange(xy_positions)
        z_vector = np.arange(z_positions)
        channel_vector = np.arange(channels)
            
        # Use meshgrid to generate the matrices for all combinations, accommodating the different sizes
        xx, yy, zz, ww = np.meshgrid(time_vector, xy_vector, z_vector, channel_vector, indexing='ij')

        # Reshape the matrices into vectors and stack them into a matrix where each row is a combination
        combinations = np.vstack([xx.ravel(), yy.ravel(), zz.ravel(), ww.ravel()]).T
        num_combinations = np.shape(combinations)[0]    
        
        selector_array = np.array([time_true,xy_true,z_true,channel_true])
        bool_selector = selector_array == 1
        
        # set in beginning
        num_chunks = int(np.ceil((len(combinations)/chunk_size)))
        
        initial_take = 0
        index_in_chunk = list()
        
        for current_chunk in range(num_chunks):
            temp_list = list()
            for current_take in range(chunk_size):
                try:
                    current_combination = combinations[initial_take,:]
                    temp_list.append(current_combination)
                    initial_take = initial_take + 1
                except:
                    break
            index_in_chunk.append(temp_list)
                   
        for current_chunk in range(num_chunks):
            current_list = index_in_chunk[current_chunk]
            dask_chunk_storage = np.ndarray(shape=(len(current_list),y_pixel_number,x_pixel_number),dtype=np.uint16)
            for current_entry in range(len(current_list)):
                current_combination = current_list[current_entry]
                sub_take = current_combination[np.array(bool_selector)]
                slicing_tuple = tuple(sub_take) + (slice(None), slice(None))
                dask_chunk_storage[current_entry,:,:] = np.asarray(dask_image_stack[slicing_tuple])
                
            with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
                for current_entry in range(len(current_list)):
                    executor.submit(process_chunk, output_path, prefix, dask_chunk_storage, current_list, current_entry)
                    
        #with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
            #for combination_index in range(num_combinations):
                #executor.submit(process_combination, output_path, prefix, dask_image_stack, bool_selector, combinations, combination_index)
                #process_combination(output_path, prefix, dask_image_stack, bool_selector, combinations, combination_index)
        
        #num_workers = int(number_worker) if number_worker != 'MusclePower' else None
        #with ProcessPoolExecutor(num_workers) as executor:
            #futures = [executor.submit(process_combination, output_path, prefix, dask_image_stack, bool_selector, combinations, combination_index) for combination_index in range(num_combinations)]
        
        #for current_xy in range(xy_positions):
            #sub_image_stack = np.asarray(dask_image_stack[:, current_xy, :, :, :, :]) if time else np.asarray(dask_image_stack[current_xy, :, :, :, :]) 
            #if prefix_indicator == 'Yes':               
                #chunk_prefix = ''.join([prefix_list[prefix_take],'_'])               
            #else:
                #chunk_prefix = ''
            
            #if prefix_indicator == 'Yes':  
                #if ((current_xy + 1) % sub_chunks == 0):
                    #prefix_take = prefix_take + 1

        bar()
       
# Say goodbye
print('\033[1;34;40mSubroutine "2" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')