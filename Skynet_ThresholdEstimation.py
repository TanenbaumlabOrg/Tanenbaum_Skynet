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
print('\033[1;34;40mYou accessed subroutine "7": Estimate an appropriate threshold for FISH spot detection. \033[1;37;40m \n')

# Range of threshold stepping
print('')
print('\033[2;37;40mPlease ensure you have saved examples images in "PARENTFOLDER"/SPOTDETECTION/IMAGESUBSET \033[1;37;40m \n')  

# Inputs
# Location above "NIS" folder
print('')
BasePath = input('\033[2;37;40mPlease provide the location of the parent folder: \033[1;37;40m \n')
# Set PixelSize
print('')
PixelSize = float(input('\033[2;37;40mWhat is the pixel size (1d, in nm): \033[1;37;40m \n'))
# Guess object radius
print('')
ObjectRadius = float(input('\033[2;37;40mWhat suspected radius of the spots (in nm): \033[1;37;40m \n'))
# Radius of Segmentation
print('')
SegmentationRadius = int(input('\033[2;37;40mHow large do you wish the segmentation radius for visualization to be (1,2...N): \033[1;37;40m \n'))
# Side By Side
print('')
ComparisonMode = input('\033[2;37;40mDo you wish to also save a side-by-side comparison with Spot segmentation overlay ("Yes","No")? \033[1;37;40m \n')
# Threshold range mode
print('')
ThresholdRange = input('\033[2;37;40mDo you wish the center of threshold estimation be determined automatically (will vary per image) or be provided value ("Auto","Manual"): \033[1;37;40m \n')
if ThresholdRange == 'Manual':
    print('')
    ThresholdCenter = int(input('\033[2;37;40mWhich integer do you wish to be the center of threshold estimation (Recom: ~140):  \033[1;37;40m \n'))
# Threshold Increments
print('')
ThresholdIncrements = int(input('\033[2;37;40mIn which step size do you want to assess thresholds from center (Recom: 5-10): \033[1;37;40m \n'))  
# Range of threshold stepping
print('')
ThresholdStep = int(input('\033[2;37;40mHow many steps do you want to explore thresholds in both directions (1,2....N): \033[1;37;40m \n'))      
# How many workers will be used for parallelization
print('')
NumberWorker = input('\033[2;37;40mFinally, how big is your tool (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
print('')
if NumberWorker == 'MusclePower':  
    print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
else:
   print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please not that the T-800 has been dispatched to eradicate you from the timeline.  \033[1;37;40m \n')
  


# Make strings for subfolders
PathINPUT = '/'.join([BasePath, 'SPOTDETECTION', 'IMAGESUBSET'])
PathOUTPUT = '/'.join([BasePath, 'SPOTDETECTION', 'THRESHOLDS'])
PathTemp = '/'.join([BasePath, 'SPOTDETECTION', 'TEMP'])
PathTempIMAGES = '/'.join([BasePath, 'SPOTDETECTION', 'TEMP','IMAGES'])
PathTempSPOTS = '/'.join([BasePath, 'SPOTDETECTION', 'TEMP','SPOTS'])

if not os.path.exists(PathINPUT):
    print('')
    print('\033[1;31;40mYou are a moron. The path does not exist. \033[1;37;40m \n')
    print('\033[1;31;40mTry again with the correct path. \033[1;37;40m \n')
    sys.exit()
else:
    print('')
    print('\033[1;33;40mFor now, we will acknowledge your supremacy and are processing your request. Standby. \033[1;37;40m \n')

# Create PNG folder if not already existing
if not os.path.exists(PathOUTPUT):
        os.mkdir(PathOUTPUT)

# Create PNG folder if not already existing
if not os.path.exists(PathTemp):
        os.mkdir(PathTemp)

# Create PNG folder if not already existing
if not os.path.exists(PathTempIMAGES):
        os.mkdir(PathTempIMAGES)

# Create PNG folder if not already existing
if not os.path.exists(PathTempSPOTS):
        os.mkdir(PathTempSPOTS)
# Define Function

def Save_Thresholds(PathOUTPUT, PathTempSPOTS, PreFix, CurrentImage, FilteredImage, PixelSize, ObjectRadius, Mask, CurrentThreshold, SegmentationRadius):
   
    # Detect spots
    Spots, _ = detection.spots_thresholding(FilteredImage, Mask, CurrentThreshold)
                 
    Distance = SegmentationRadius
    Make_SegmentationImage(PathOUTPUT,CurrentImage,Spots,PreFix,Distance, CurrentThreshold)
    Save_SpotsTemp(PathTempSPOTS, Spots, PreFix, CurrentThreshold)
 
def Save_SpotsTemp(PathTempSPOTS ,Spots, PreFix, CurrentThreshold):
    
    SpotPandas = pd.DataFrame(Spots)
    ThresholdString = '\n'.join(['{0:03}'.format(int(CurrentThreshold))])
    SpotSaveName = ''.join([PathTempSPOTS,'/',PreFix,'_','T',ThresholdString,'.csv'])
    SpotPandas.to_csv(SpotSaveName)
    

def Make_SegmentationImage(PathOUTPUT,CurrentImage, Spots, PreFix, Distance, CurrentThreshold):
    SegmentationImage = np.zeros_like(CurrentImage)
    YDimensionImage, XDimensionImage = SegmentationImage.shape[:2]

    for YCoord, XCoord in Spots:
        YRange = np.clip(np.arange(YCoord - Distance, YCoord + Distance + 1), 0, YDimensionImage - 1)
        XRange = np.clip(np.arange(XCoord - Distance, XCoord + Distance + 1), 0, XDimensionImage - 1)

        YPoints, XPoints = np.meshgrid(YRange, XRange)
        ManhattanDistance = np.abs(YPoints - YCoord) + np.abs(XPoints - XCoord)

        SegmentationImage[YPoints[ManhattanDistance == Distance], XPoints[ManhattanDistance == Distance]] = 1
        
    SaveSegmentationImage = im.fromarray(SegmentationImage)
    ThresholdString = '\n'.join(['{0:03}'.format(int(CurrentThreshold))])
    SegmentationSaveName = ''.join([PathOUTPUT,'/','T',ThresholdString,'_',PreFix,'.png'])
    SaveSegmentationImage.save(SegmentationSaveName)    
    
    # Plot side by side.. somehow
    #SideBySideName = ''.join([PathOUTPUT,'/','Comparison_T',ThresholdString,'_',PreFix,'.png'])
    #sleep(25)
    #plot.plot_detection(CurrentImage, Spots, contrast=True, path_output = SideBySideName)
    #sleep(25)
    #matplotlib.pyplot.close()

def Make_ComparisonImage(PathOUTPUT, CurrentImage, Spots, PreFix, TSuffix):

    SideBySideName = ''.join([PathOUTPUT,'/','Comparison_',TSuffix,'_',PreFix,'.png'])  
    plot.plot_detection(CurrentImage, Spots, contrast=True, path_output = SideBySideName)
    matplotlib.pyplot.close()
    
def Prepare_Processing(PathINPUT, PathOUTPUT, PathTempSPOTS, CurrentFile, PixelSize, ObjectRadius, ThresholdRange, ThresholdCenter, ThresholdIncrements, SegmentationRadius):
    # Get Prefix
    PreFix = CurrentFile[0:len(CurrentFile)-4]
    
    # Read current image
    CurrentImage = stack.read_image('/'.join([PathINPUT,CurrentFile]))
    
    # Determine spot parameters
    # spot radius
    spot_radius_px = detection.get_object_radius_pixel(
        voxel_size_nm=(PixelSize, PixelSize), 
        object_radius_nm=(ObjectRadius, ObjectRadius), 
        ndim=2)

    # Apply LoG Filter
    FilteredImage = stack.log_filter(CurrentImage,spot_radius_px)
    
    # Detect local maxima
    Mask = detection.local_maximum_detection(FilteredImage, min_distance=spot_radius_px)
    
    # Do an automated thresholding
    if ThresholdRange == 'Auto':
        ThresholdCenter = detection.automated_threshold_setting(FilteredImage, Mask)
    elif ThresholdRange == 'Manual': 
        ThresholdCenter = ThresholdCenter
    # Now loop over different thresholds in increments starting from the automatically identified one
    Increment = ThresholdIncrements
    ThresholdList = [(ThresholdCenter - i * Increment) for i in range(ThresholdStep,0,-1)] + [(ThresholdCenter + i * Increment) for i in range(1, ThresholdStep+1)]
    for CurrentThreshold in ThresholdList:
        #executor.submit(Save_Thresholds, PathOUTPUT, PreFix, CurrentImage, FilteredImage, PixelSize, ObjectRadius, Mask, CurrentThreshold, SegmentationRadius)
        Save_Thresholds(PathOUTPUT, PathTempSPOTS, PreFix, CurrentImage, FilteredImage, PixelSize, ObjectRadius, Mask, CurrentThreshold, SegmentationRadius)  
       
def Prepare_ProcessingMinmal(PathINPUT, CurrentFile):
    
    # Get Prefix
    PreFix = CurrentFile[0:len(CurrentFile)-4]
    
    # Read current image
    CurrentImage = stack.read_image('/'.join([PathINPUT,CurrentFile]))
    
    return PreFix, CurrentImage
              
# End of defining functions

# Main body
# Detect number of images in Subset
ImageNames = [CurrentFile for CurrentFile in listdir(PathINPUT) if isfile('/'.join([PathINPUT, CurrentFile]))]
print('\033[1;34;40mWe identified',str(len(ImageNames)),'unique Image files. \033[1;37;40m \n')

    
with alive_bar(len(ImageNames)) as bar:
    with ThreadPoolExecutor(int(NumberWorker) + 4 if NumberWorker != 'MusclePower' else None) as executor:
        # Submit all tasks to the executor at once
        Futures = [executor.submit(Prepare_Processing, PathINPUT, PathOUTPUT, PathTempSPOTS, CurrentFile, PixelSize, ObjectRadius, ThresholdRange, ThresholdCenter, ThresholdIncrements, SegmentationRadius) for CurrentFile in ImageNames]

        # Wait for all tasks to complete
        for Future in concurrent.futures.as_completed(Futures):
            bar()  # Update progress bar for each completed task        

# Now do separate looping for bloody comparison image....
if ComparisonMode == 'Yes':
    CSVNames = [CurrentFile for CurrentFile in listdir(PathTempSPOTS) if isfile('/'.join([PathTempSPOTS, CurrentFile]))]
    with alive_bar(len(ImageNames)) as bar:
        for CurrentFile in ImageNames:
            PreFix, CurrentImage = Prepare_ProcessingMinmal(PathINPUT, CurrentFile)
            # get all csv with the PreFix
            SpotCountFiles = [x for x in CSVNames if re.search(PreFix, x)]
            for CurrentSpotCountFile in SpotCountFiles:
                FullSuffix = CurrentSpotCountFile[len(CurrentSpotCountFile) - 8:]
                TSuffix = FullSuffix[0:len(FullSuffix)-4]
                SpotCount = pd.read_csv('/'.join([PathTempSPOTS,CurrentSpotCountFile]))
                Spots = SpotCount.iloc[:,1:3].values
                Make_ComparisonImage(PathOUTPUT, CurrentImage, Spots, PreFix, TSuffix)
            bar()
        
# Say goodbye
print('\033[1;34;40mSubroutine "6" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')
