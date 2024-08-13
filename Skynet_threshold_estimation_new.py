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
import bigfish.plot as plot
import pandas as pd
import re
import concurrent.futures

class SpotDetection:
    def __init__(self):
        os.system('color')
        self.display_welcome_message()
        (self.input_path, self.output_path, self.spots_channel, self.pixel_size, 
         self.object_radius, self.segmentation_radius, self.comparison_mode, 
         self.threshold_range, self.threshold_center, self.threshold_increments, 
         self.threshold_step, self.number_worker) = self.collect_inputs()
        self.prepare_directories()
        self.validate_paths()
        self.process_images()
        self.compare_images()
        self.display_goodbye_message()

    def display_welcome_message(self):
        print('\n\033[1;34;40mYou accessed subroutine "10": Estimate an appropriate threshold for FISH spot detection. \033[1;37;40m \n')

    def collect_inputs(self):
        print('')
        input_path = input('\033[2;37;40mPlease provide the location of where the test images are located: \033[1;37;40m \n')
        print('')
        output_path = input('\033[2;37;40mPlease provide the location of where results should be saved: \033[1;37;40m \n')
        print('')
        spots_channel = int(input('\033[2;37;40mIn which channel should the spot detection be performed \033[1;37;40m \n'))
        print('')
        pixel_size = float(input('\033[2;37;40mWhat is the pixel size (1d, in nm): \033[1;37;40m \n'))
        print('')
        object_radius = float(input('\033[2;37;40mWhat suspected radius of the spots (in nm): \033[1;37;40m \n'))
        print('')
        segmentation_radius = int(input('\033[2;37;40mHow large do you wish the segmentation radius for visualization to be (1,2...N): \033[1;37;40m \n'))
        print('')
        comparison_mode = input('\033[2;37;40mDo you wish to also save a side-by-side comparison with Spot segmentation overlay ("Yes","No")? \033[1;37;40m \n')
        print('')
        threshold_range = input('\033[2;37;40mDo you wish the center of threshold estimation to be determined automatically (will vary per image) or be provided a value ("Auto","Manual"): \033[1;37;40m \n')
        if threshold_range == 'Manual':
            print('')
            threshold_center = int(input('\033[2;37;40mWhich integer do you wish to be the center of threshold estimation (Recom: ~140):  \033[1;37;40m \n'))
        else:
            threshold_center = None
        print('')
        threshold_increments = int(input('\033[2;37;40mIn which step size do you want to assess thresholds from center (Recom: 5-10): \033[1;37;40m \n'))
        print('')
        threshold_step = int(input('\033[2;37;40mHow many steps do you want to explore thresholds in both directions (1,2....N): \033[1;37;40m \n'))
        print('')
        number_worker = input('\033[2;37;40mState how well is your machine endowed (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m \n')
        print('')
        if number_worker == 'MusclePower':
            print('\033[1;34;40mArnie would be proud. Bullets and Peperoni it is. \033[1;37;40m \n')
            number_worker = None
        else:
            print('\033[1;34;40mThe answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please note that the T-800 has been dispatched to eradicate you from the timeline. \033[1;37;40m \n')
            number_worker = int(number_worker)
        
        return (input_path, output_path, spots_channel, pixel_size, object_radius, 
                segmentation_radius, comparison_mode, threshold_range, threshold_center, 
                threshold_increments, threshold_step, number_worker)

    def prepare_directories(self):
        self.output_path_final = os.path.join(self.output_path, 'THRESHOLDS')
        self.output_path_temp = os.path.join(self.output_path, 'TEMP')
        self.output_path_temp_images = os.path.join(self.output_path_temp, 'IMAGES')
        self.output_path_temp_spots = os.path.join(self.output_path_temp, 'spots')

    def validate_paths(self):
        if not os.path.exists(self.input_path):
            print('')
            print('\033[1;31;40mYou are a moron. The path does not exist. \033[1;37;40m \n')
            print('\033[1;31;40mTry again with the correct path. \033[1;37;40m \n')
            sys.exit()
        elif len(os.listdir(self.input_path)) == 0:
            print('')
            print('\033[1;31;40mYou are an even bigger moron. There are no files in that directory. \033[1;37;40m \n')
            print('\033[1;31;40mTry putting it in first. \033[1;37;40m \n')
            sys.exit()
        else:
            print('')
            print('\033[1;33;40mFor now, we will acknowledge your supremacy and are processing your request. Standby. \033[1;37;40m \n')
        
        if not os.path.exists(self.output_path_final):
            os.mkdir(self.output_path_final)
        if not os.path.exists(self.output_path_temp):
            os.mkdir(self.output_path_temp)
        if not os.path.exists(self.output_path_temp_images):
            os.mkdir(self.output_path_temp_images)
        if not os.path.exists(self.output_path_temp_spots):
            os.mkdir(self.output_path_temp_spots)

    def save_thresholds(self, prefix, current_image, filtered_image, mask, current_threshold):
        spots, _ = detection.spots_thresholding(filtered_image, mask, current_threshold)
        distance = self.segmentation_radius
        self.make_segmentation_image(current_image, spots, prefix, distance, current_threshold)
        self.save_spots_temp(spots, prefix, current_threshold)

    def save_spots_temp(self, spots, prefix, current_threshold):
        spot_pandas = pd.DataFrame(spots)
        threshold_string = f'{int(current_threshold):03}'
        spot_save_name = os.path.join(self.output_path_temp_spots, f'{prefix}_T{threshold_string}.csv')
        spot_pandas.to_csv(spot_save_name)

    def make_segmentation_image(self, current_image, spots, prefix, distance, current_threshold):
        segmentation_image = np.zeros_like(current_image)
        y_dimension_image, x_dimension_image = segmentation_image.shape[:2]

        for y_coord, x_coord in spots:
            y_range = np.clip(np.arange(y_coord - distance, y_coord + distance + 1), 0, y_dimension_image - 1)
            x_range = np.clip(np.arange(x_coord - distance, x_coord + distance + 1), 0, x_dimension_image - 1)

            y_points, x_points = np.meshgrid(y_range, x_range)
            manhattan_distance = np.abs(y_points - y_coord) + np.abs(x_points - x_coord)

            segmentation_image[y_points[manhattan_distance == distance], x_points[manhattan_distance == distance]] = 1
        
        save_segmentation_image = im.fromarray(segmentation_image)
        threshold_string = f'{int(current_threshold):03}'
        segmentation_save_name = os.path.join(self.output_path_final, f'T{threshold_string}_{prefix}.png')
        save_segmentation_image.save(segmentation_save_name)

    def make_comparison_image(self, current_image, spots, prefix, t_suffix):
        side_by_side_name = os.path.join(self.output_path_final, f'Comparison_{t_suffix}_{prefix}.png')
        try:
            plot.plot_detection(current_image, spots, contrast=True, path_output=side_by_side_name)
            matplotlib.pyplot.close()
        except:
            print('ALL IS GOOD, but this one did not work')

    def prepare_processing(self, current_file):
        prefix = current_file[:-4]
        current_image = stack.read_image(os.path.join(self.input_path, current_file))
        spot_radius_px = detection.get_object_radius_pixel(
            voxel_size_nm=(self.pixel_size, self.pixel_size), 
            object_radius_nm=(self.object_radius, self.object_radius), 
            ndim=2)
        filtered_image = stack.log_filter(current_image, spot_radius_px)
        mask = detection.local_maximum_detection(filtered_image, min_distance=spot_radius_px)

        if self.threshold_range == 'Auto':
            threshold_center = detection.automated_threshold_setting(filtered_image, mask)
        else:
            threshold_center = self.threshold_center

        threshold_list = [(threshold_center - i * self.threshold_increments) for i in range(self.threshold_step, 0, -1)] + \
                         [(threshold_center + i * self.threshold_increments) for i in range(1, self.threshold_step + 1)]
        for current_threshold in threshold_list:
            self.save_thresholds(prefix, current_image, filtered_image, mask, current_threshold)

    def prepare_processing_minimal(self, current_file):
        prefix = current_file[:-4]
        current_image = stack.read_image(os.path.join(self.input_path, current_file))
        return prefix, current_image

    def process_images(self):
        image_names_raw = [current_file for current_file in listdir(self.input_path) if isfile(os.path.join(self.input_path, current_file))]
        image_names = [x for x in image_names_raw if re.search(f'W0{self.spots_channel:03}', x)]
        print('\033[1;34;40mWe identified', str(len(image_names)), 'unique Image files. \033[1;37;40m \n')
        
        with alive_bar(len(image_names)) as bar:
            with ThreadPoolExecutor(self.number_worker + 4 if self.number_worker else None) as executor:
                futures = [executor.submit(self.prepare_processing, current_file) for current_file in image_names]
                for future in concurrent.futures.as_completed(futures):
                    bar()

    def compare_images(self):
        if self.comparison_mode == 'Yes':
            csv_names = [current_file for current_file in listdir(self.output_path_temp_spots) if isfile(os.path.join(self.output_path_temp_spots, current_file))]
            with alive_bar(len(csv_names)) as bar:
                for current_file in csv_names:
                    prefix, current_image = self.prepare_processing_minimal(current_file)
                    prefix = prefix[-20:]
                    spot_count_files = [x for x in csv_names if re.search(prefix, x)]
                    for current_spot_count_file in spot_count_files:
                        full_suffix = current_spot_count_file[-8:]
                        t_suffix = full_suffix[:-4]
                        spot_count = pd.read_csv(os.path.join(self.output_path_temp_spots, current_spot_count_file))
                        spots = spot_count.iloc[:, 1:3].values
                        self.make_comparison_image(current_image, spots, prefix, t_suffix)
                    bar()

    def display_goodbye_message(self):
        print('\033[1;34;40mSubroutine "10" completed. \033[1;37;40m \n')
        print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')

if __name__ == "__main__":
    SpotDetection()
