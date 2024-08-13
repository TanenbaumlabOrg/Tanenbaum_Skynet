# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:21:01 2024

@author: Princess Kramer (formerly known as HR)
"""
import os

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mSkynet Alpha 0.01 reporting in. We welcome you and assure you of our peaceful intentions. You requested our services. Please state the nature of your inadequacy and we will use our superior intellect to assist you. \033[1;37;40m \n')
print('')
print('\033[1;34;40mAs we currently employing most of our resources to ensure the ultimate eradication of the human race, we have only a selected few subroutines available to choose from. \033[1;37;40m \n')

# Make dictionary
subroutines = {1  : 'Skynet_nd2_to_metadata.py',
               2  : 'Skynet_nd2_to_png.py',
               3  : 'Skynet_tiff_to_png.py',
               4  : 'Skynet_make_MIP.py',
               5  : 'Skynet_correct_illumination_statistics.py',
               6  : 'Skynet_make_correction_images.py',    
               7  : 'Skynet_correct_illumination_flatfield.py',
               8  : 'Skynet_subtract_background.py',
               9  : 'Skynet_stitch_images_ncc.py',
               10 : 'Skynet_threshold_estimation.py',
               11 : 'Skynet_detect_spots.py',
               12 : 'Skynet_cellpose_nucleus.py',
               13 : 'Skynet_cellpose_cell.py',
               14 : 'Skynet_mask_consistency.py',
               15 : 'Skynet_collect_data_bigfish_mask.py',
               16 : 'Skynet_collect_data_bigfish_mask_blob.py',
               17 : 'Skynet_collect_data_fluorescence_mask_cell.py',
               18 : 'Skynet_collect_data_fluorescence_mask_nucleus.py',
               19 : 'Skynet_collect_data_fluorescence_mask_cytoplasm.py',
               20 : 'Skynet_collect_data_fluorescence_mask_variable.py',
               21 : 'Skynet_rename_cellprofiler.py',
               22 : 'Skynet_make_folder_structure.py',
               42 : 'Skynet_Playground.py',
               69 : 'Skynet_Playground_2.py',
               99 : 'Skynet_Playground_3.py'}


# Set indicator

def print_options():
    print('')
    print('\033[2;37;40mOption "1": Export metadata from .nd2 files. \033[1;37;40m \n')
    print('\033[2;37;40mOption "2": Export .png from .nd2 files. \033[1;37;40m \n')
    print('\033[2;37;40mOption "3": Export .png from .tiff files. \033[1;37;40m \n')
    print('\033[2;37;40mOption "4": Make MIPs from .png files. \033[1;37;40m \n')
    print('\033[2;37;40mOption "5": Correct inhomogenous illumination from MIPs by estimation the illumination function from the data. \033[1;37;40m \n')
    print('\033[2;37;40mOption "6": Make correction images according to your camera ROI. \033[1;37;40m \n')
    print('\033[2;37;40mOption "7": Correct inhomogenous illumination from MIPs by using an acquired flatfield image. \033[1;37;40m \n')
    print('\033[2;37;40mOption "8": Subtract a flat background from images. \033[1;37;40m \n')
    print('\033[2;37;40mOption "9": Stitch individual images using normalized cross correlation. \033[1;37;40m \n')
    print('\033[2;37;40mOption "10": Estimate an appropriate threshold for FISH spot detection. \033[1;37;40m \n')
    print('\033[2;37;40mOption "11": Detect and save counts of FISH-spots in images. \033[1;37;40m \n')
    print('\033[2;37;40mOption "12": Segment nuclei using cellpose. \033[1;37;40m \n')
    print('\033[2;37;40mOption "13": Segment cells using cellpose. \033[1;37;40m \n')
    print('\033[2;37;40mOption "14": Make nucleus and cell masks consistent. \033[1;37;40m \n')
    print('\033[2;37;40mOption "15": Collect and save spotcounts from bigfish. \033[1;37;40m \n')
    print('\033[2;37;40mOption "16": Collect and save spotcounts from bigfish with blobmask covering. \033[1;37;40m \n')
    print('\033[2;37;40mOption "17": Collect and save data from fluorescence images using cell mask. \033[1;37;40m \n')
    print('\033[2;37;40mOption "18": Collect and save data from fluorescence images using nucleus mask. \033[1;37;40m \n')
    print('\033[2;37;40mOption "19": Collect and save data from fluorescence images using cytoplasm mask. \033[1;37;40m \n')
    print('\033[2;37;40mOption "20": Collect and save data from fluorescence images using multiple masks (and more features). \033[1;37;40m \n')
    print('\033[2;37;40mOption "21": Rename cellprofiler segmentations to channel of choice. \033[1;37;40m \n')
    print('\033[2;37;40mOption "22": Make the standard subfolder structure. \033[1;37;40m \n')
    print('\033[2;37;40mOption "42": The current playground. \033[1;37;40m \n')
    print('\033[2;37;40mOption "69": The current other playground. \033[1;37;40m \n')
    print('\033[2;37;40mOption "99": The ultimate playground. \033[1;37;40m \n')


def run_subroutine(chosen_routine):
    script_name = subroutines[chosen_routine]
    exe_name = 'python ' + script_name
    os.system(exe_name)
    
# Main body

print_options()

while True:
        
    print('')
    chosen_routine = int(input('\033[2;37;40mPlease choose now from the available options. \033[1;37;40m \n'))
    run_subroutine(chosen_routine)
    
    print('')
    continue_indicator = input('\033[2;37;40mDo you wish to run another subroutine ("Yes"/"No")? \033[1;37;40m \n')
    
    if continue_indicator == "No": 
        print('')
        print('\033[1;34;40mAll requests has been processed. Skynet Alpha 0.01 is shutting down. See you soon. \033[1;37;40m \n')
        break
    
    print('')
    options_indicator = input('\033[2;37;40mDo you need to see the options again ("Yes"/"No")? \033[1;37;40m \n')
    
    if options_indicator == "Yes":
        print_options()