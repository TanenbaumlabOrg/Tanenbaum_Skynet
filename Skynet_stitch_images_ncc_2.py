# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""

import numpy as np
from PIL import Image as im
from os import listdir
from os.path import isfile, join
import os
import re
import cv2
import sys
from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor
import m2stitch
import concurrent.futures
import contextlib

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mSkynet Alpha 0.01 reporting in. We welcome you and assure you of our peaceful intentions. You accessed our services to correct inhomogenous illumination of already maximum projected .png files using Schmaexis Flatfields. \033[1;37;40m \n')

# Inputs
# Location above "ToStitch" folder
print('')
BasePath = input('\033[2;37;40mPlease provide the location of the parent folder: \033[1;37;40m \n')

# Number of channels to correct
print('')
NumberChannel = int(input('\033[2;37;40mPlease provide the number of channels which need to be stitched: \033[1;37;40m \n'))

# Reference channel to calculate stitching
print('')
ReferenceChannel = int(input('\033[2;37;40mPlease provide the reference channel from which stitching parameters will be calculated: \033[1;37;40m \n'))

# How many rows were acquired in the experiment?
print('')
AcquiredRows = int(input('\033[2;37;40mPlease provide the number of rows which were acquired: \033[1;37;40m \n'))

# How many columns were acquired in the experiment?
print('')
AcquiredColumns = int(input('\033[2;37;40mPlease provide the number of columns which were acquired: \033[1;37;40m \n'))

# determine snake or normal acquisition
print('')
AcquisitionType = input('\033[2;37;40mHow were images acquired - in Snake or Normal mode: \033[1;37;40m \n')

# How many workers will be used for parallelization
print('')
NumberWorker = input('\033[2;37;40mFinally, how big is your tool (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
print('')
if NumberWorker == 'MusclePower':  
    print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
else:
   print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n')
# End of inputs

# Start of script
PathILLCORR = BasePath + '/ILLCORR/';
PathSTITCHED = BasePath + '/STITCHED/';

if not os.path.exists(PathILLCORR):
    print('')
    print('\033[1;31;40mYou are a moron. The path does not exist. \033[1;37;40m \n')
    print('\033[1;31;40mTry again with the correct path. \033[1;37;40m \n')
    sys.exit()
else:
    print('')
    print('\033[1;33;40mFor now, we will acknowledge your supremacy and are processing your request. Standby. \033[1;37;40m \n')
    
# Check if PNG folder exists and if not, make it
if os.path.exists(PathSTITCHED) == False:
    os.mkdir(PathSTITCHED);

# Get important num
SumPositions = AcquiredRows * AcquiredColumns
NumberDigits = len(str(SumPositions))

# Make TileIndex
TileIndex = [int(CurrentTile) for CurrentTile in range(1, SumPositions + 1)]

# Make RowIndex
RowIndex = [int(CurrentRow) for CurrentRow in range(1, AcquiredRows + 1) for _ in range(AcquiredColumns)]

# Make ColumnIndex
ColumnIndex = [
    int((CurrentColumn - (AcquiredColumns + 1)) * -1) if AcquisitionType == 'Snake' and CurrentRow % 2 == 0 else int(CurrentColumn)
    for CurrentRow in range(1, AcquiredRows + 1)
    for CurrentColumn in range(1, AcquiredColumns + 1)
]


# Define functions
def Stitch_Channel(PathILLCORR, PathSTITCHED, SubString, CurrentChannel, size_y, size_x, result_df):
    
    CurrentGroupToCorrect = [x for x in ILLCORRNames if re.search(f'W0{CurrentChannel+1:03}', x)]
    ImagesGroupToCorrect = [x for x in CurrentGroupToCorrect if re.search(SubString, x)]
    
    EmptyImage = np.array([cv2.imread(join(PathILLCORR, img), cv2.IMREAD_UNCHANGED)[0:900, 0:700] for img in ImagesGroupToCorrect], dtype='uint16')

    stitched_image_size = (
        result_df["y_pos2"].max() + size_y,
        result_df["x_pos2"].max() + size_x,
    )
    
    stitched_image = np.zeros_like(EmptyImage, shape=stitched_image_size)
    
    for i, row in result_df.iterrows():
        stitched_image[
            row["y_pos2"] : row["y_pos2"] + size_y,
            row["x_pos2"] : row["x_pos2"] + size_x,
        ] = EmptyImage[i]

    ImagePNG = im.fromarray(stitched_image)
    SaveNameFull = join(PathSTITCHED, ImagesGroupToCorrect[0])
    ImagePNG.save(SaveNameFull)

def Calculate_Stitch(ReferenceGroup, CurrentGroup, PathILLCORR, PathSTITCHED):
    
    # Get just relevant string parts
    SubString = CurrentGroup[:-24]

    # Find all images belonging to this group
    ImagesGroup = [x for x in ReferenceGroup if re.search(SubString, x)]

    # Load into image stack
    EmptyImage = np.array([cv2.imread(PathILLCORR + CurrentImage, cv2.IMREAD_UNCHANGED)[0:900, 0:700] for CurrentImage in ImagesGroup])
    
    # Convert to 16bit image
    BitImage = EmptyImage.astype('uint16')
    
    # Try stitching with different Thresholds
    for ncc_threshold in (0.6, 0.55 ,0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.01):
        try:
            result_df, _ = m2stitch.stitch_images(BitImage, RowIndex, ColumnIndex, row_col_transpose=False, ncc_threshold=ncc_threshold)
            break
        except Exception:
            pass
        else:
            raise RuntimeError('Failed with unknown exception. Vogel. Vollhorst.')

    # Generate the y_pos2 and x_pos2 variables
    result_df["y_pos2"] = result_df["y_pos"] - result_df["y_pos"].min()
    result_df["x_pos2"] = result_df["x_pos"] - result_df["x_pos"].min()
    
    # Get size of the base images
    size_y, size_x = BitImage.shape[1:3]

    for CurrentChannel in range(NumberChannel):
        Stitch_Channel(PathILLCORR, PathSTITCHED, SubString, CurrentChannel, size_y, size_x, result_df)
    
   
# Main code body
# Get names of all png files in the specified folder
ILLCORRNames = [CurrentFile for CurrentFile in listdir(PathILLCORR) if isfile(join(PathILLCORR,CurrentFile))];
NumberILLCORR = np.shape(ILLCORRNames)[0];

# Get all images with the reference channel
ReferenceGroup = [x for x in ILLCORRNames if re.search(f'W0{ReferenceChannel:03}', x)]

# Get the relevant group names
CurrentGroupReal = [x for x in ReferenceGroup if re.search('P0001', x)];
NumberGroups = np.shape(CurrentGroupReal)[0];

# Actual Loop
#with alive_bar(NumberGroups) as bar:
with ThreadPoolExecutor(int(NumberWorker) + 4 if NumberWorker != 'MusclePower' else None) as executor:        
    # Submit all tasks to the executor at once    
    for CurrentGroup in CurrentGroupReal:
        with contextlib.redirect_stdout(None):
            executor.submit(Calculate_Stitch, ReferenceGroup, CurrentGroup, PathILLCORR, PathSTITCHED)

        # Wait for all tasks to complete
        #for Future in concurrent.futures.as_completed(Futures):
            #bar()  # Update progress bar for each completed task
        
# Say goodbye
print('\033[1;34;40mRequest has been processed. Skynet Alpha 0.01 is shutting down. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')
