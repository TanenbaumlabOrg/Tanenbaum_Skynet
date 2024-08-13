# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
import nd2
from os import listdir
from os.path import isfile
import os
import sys
from alive_progress import alive_bar
import pandas as pd


os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "1": Export metadata from .nd2 files. \033[1;37;40m \n')

# Start of inputs
# Location of the NIS folder
print('')
input_path = input('\033[2;37;40mPlease provide the location of the .nd2 files: \033[1;37;40m \n')
# Location of the metadata
print('')
output_path = input('\033[2;37;40mPlease provide the location to which you wish metadata to be exported: \033[1;37;40m \n')
# End of outputs


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

def get_nd2_meta(path_nd2: str):
    '''
    Input:
        path_nd2: location of nd2 file to parse

    Return:
        sizes [dict]
        channels [list]
        positions [np]
        px_size [float]
    '''
    positions = []
    with (nd2.ND2File(path_nd2)) as data_img:
        # nd2 dimensions and sizes
        sizes = data_img.sizes
        
        # channel info
        channels = get_channels(data_img.metadata.channels, sizes)

        # parse positional metadata per image
        meta_frame = data_img.frame_metadata
        image_number = get_image_number(sizes)
        for i in range(image_number):
            meta_channels = getattr(meta_frame(i), 'channels')
            meta_stageposition = get_nested_attribute(meta_channels[0], 'position/stagePositionUm')
            positions.append(meta_stageposition)
        positions = pd.DataFrame(positions, columns = ["X", "Y", "Z"])
        positions[['iT', 'iP', 'iZ']] = [[t, p, z] for t in range(sizes.get('T', 1)) for p in range(sizes.get('P', 1)) for z in range(sizes.get('Z', 1))]

        # pixel size
        px_size = get_nested_attribute(getattr(meta_frame(0), 'channels')[0], 'volume/axesCalibration')[0]

        data_img.close
    return sizes, channels, positions, px_size

def get_channels(channels: list, sizes: dict):
    list_channels = []
    if 'C' in sizes:
        for c in range(sizes['C']):
            list_channels.append(get_nested_attribute(channels[c], 'channel/name'))
    else:
        list_channels.append(get_nested_attribute(channels[0], 'channel/name'))
    return list_channels

def get_image_number(sizes: dict):
    result = 1  # Initialize the result to 1
    for key, value in sizes.items():
        if key not in ['X', 'Y', 'C']:
            result *= value
    return result

def get_nested_attribute(obj, attr_path):
    attrs = attr_path.split('/')
    for attr in attrs:
        obj = getattr(obj, attr)
    return obj

nd2_names = [current_file for current_file in listdir(input_path) if isfile('/'.join([input_path, current_file]))]
print('\033[1;34;40mWe identified',str(len(nd2_names)),'unique NIS files. \033[1;37;40m \n')

with alive_bar(len(nd2_names)) as bar: 
    for current_file in nd2_names:       
        nd2_file = nd2.ND2File('/'.join([input_path, current_file]))       
        
        time = len(nd2_file.shape) > 5
        prefix, xy_positions = current_file[0:len(current_file) - 4], nd2_file.shape[0] if not time else nd2_file.shape[1]
        z_positions, channels, y_pixel_number, x_pixel_number = nd2_file.shape[1:5] if not time else nd2_file.shape[2:6]
        time_points = nd2_file.shape[0] if time else 0 
        
        general_metadata = [['Variable','Value'],['Time_Points',time_points],['XY_Positions',xy_positions],['Z_Positions',z_positions],['Channels',channels],['Pixels_Y',y_pixel_number],['Pixels_X',x_pixel_number]]
        save_name_general = ''.join([output_path,'/',prefix,'_General_Metadata.csv']);
        pandas_general_metadata = pd.DataFrame(general_metadata)
        pandas_general_metadata.to_csv(save_name_general,header=False,index=False,sep=',')
        
        [sizes ,channel_names, positions, pixel_size] = get_nd2_meta('/'.join([input_path, current_file]))
        
        save_name_positions = ''.join([output_path,'/',prefix,'_FieldPositions_Metadata.csv']);
        positions.to_csv(save_name_positions,header=True,index=False,sep=',')
        
        channel_names_list = []
        for current_channel in range(channels):
            channel_names_list.append([current_channel+1,channel_names[current_channel],0,0])
            
            save_name_channel = ''.join([output_path,'/',prefix,'_Channel_Metadata.csv']);
            pandas_channel = pd.DataFrame(channel_names_list)
            pandas_channel.columns = ['Acquisition_Index','Name','Laser_Power','Exposure_Time']
            pandas_channel.to_csv(save_name_channel,header=True,index=False,sep=',')
            
        voxel_data = nd2_file.voxel_size()
        voxel_metadata = [['Variable_Name','Dimension_(uM)'],['Y_Dimension_Voxel',voxel_data[0]],['X_Dimension_Voxel',voxel_data[1]],['Z_Dimension_Voxel',voxel_data[2]]];
        save_name_voxel = ''.join([output_path,'/',prefix,'_Voxel_Metadata.csv']);
        pandas_voxel = pd.DataFrame(voxel_metadata)
        pandas_voxel.to_csv(save_name_voxel,header=False,index=False,sep=',')
        
        
        nd2_file.close()
        bar()
        
# Say goodbye
print('\033[1;34;40mSubroutine "1" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')