# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:00:37 2024
Modified on Wed May 22 14:00:37 2024

@author: Princess Kramer (formerly known as HR)
"""
import os
import sys
import re
import numpy as np
import cv2
from PIL import Image as im
from os import listdir
from os.path import isfile, join
from concurrent.futures import ThreadPoolExecutor, as_completed
from alive_progress import alive_bar

os.system('color')

def print_colored_message(color_code, message):
    print(f'\033[{color_code}m{message}\033[1;37;40m')

class MIPMaker:
    def __init__(self, input_path, output_path, median_maximum, problem_channel=999, sub_z=999, single_indicator='None'):
        self.input_path = input_path
        self.output_path = output_path
        self.median_maximum = median_maximum
        self.problem_channel = problem_channel
        self.sub_z = sub_z
        self.single_indicator = single_indicator
        
        if not os.path.exists(output_path):
            os.mkdir(output_path)

    def load_images(self, current_name):
        load_name = join(self.input_path, current_name)
        return cv2.imread(load_name, cv2.IMREAD_UNCHANGED)

    def save_images(self, projection, current_base_file):
        image_png = im.fromarray(projection)
        save_name_full = join(self.output_path, current_base_file)
        image_png.save(save_name_full)
          
    def compute_projection(self, z_image_storage):
        if self.median_maximum == 'Maximum':                       
            return np.max(z_image_storage, axis=2)
        elif self.median_maximum == 'Median':
            median_projection = np.median(z_image_storage, axis=2)
            return np.array(median_projection, dtype='float32').astype('uint16')
    
    def process_images(self, y_pixel_number, x_pixel_number, z_positions, images_z_slices, deprecated_name):
        z_image_storage = np.zeros((y_pixel_number, x_pixel_number, z_positions), dtype=np.uint16)
        problem_channel_str = f'W0{self.problem_channel:03}'

        for current_z_index in range(z_positions):
            current_z = self.sub_z[current_z_index] if problem_channel_str in deprecated_name and self.single_indicator == 'Multiple' else self.sub_z if problem_channel_str in deprecated_name else current_z_index
            current_image_name = images_z_slices[current_z]
            current_image = self.load_images(current_image_name)
            z_image_storage[:, :, current_z_index] = current_image
        
        return self.compute_projection(z_image_storage)

    def make_MIP(self, current_base_file, png_names):
        deprecated_name = current_base_file[:-9]
        images_z_slices = [x for x in png_names if re.search(deprecated_name, x)]
        
        z_positions = len(self.sub_z) if f'W0{self.problem_channel:03}' in deprecated_name and self.single_indicator == 'Multiple' else 1 if f'W0{self.problem_channel:03}' in deprecated_name else len(images_z_slices)
        
        base_image = self.load_images(current_base_file)
        y_pixel_number, x_pixel_number = base_image.shape[:2]

        projection = self.process_images(y_pixel_number, x_pixel_number, z_positions, images_z_slices, deprecated_name)
        self.save_images(projection, current_base_file)

    def run(self, number_worker):
        png_names = [current_file for current_file in listdir(self.input_path) if isfile(join(self.input_path, current_file))]

        unique_groups = [x for x in png_names if re.search('Z0001', x)]
        number_groups = len(unique_groups)
        print_colored_message('1;34;40', f'We identified {number_groups} unique groups with 1 or more z-slices.\n')

        with alive_bar(number_groups) as bar:
            with ThreadPoolExecutor(int(number_worker) + 4 if number_worker != 'MusclePower' else None) as executor:
                futures = [executor.submit(self.make_MIP, current_base_file, png_names) for current_base_file in unique_groups]

                for _ in as_completed(futures):
                    bar()

def gather_inputs():
    input_path = input('\033[2;37;40mPlease provide the location of the .png files: \033[1;37;40m\n')
    output_path = input('\033[2;37;40mPlease provide the location to which you wish MIPs files to be exported: \033[1;37;40m\n')
    median_maximum = input('\033[2;37;40mDo you wish to make maximum or median projections ("Maximum"/"Median"): \033[1;37;40m\n')
    substack_indicator = input('\033[2;37;40mAny channels from which you only want to project a smaller number of slices ("Yes/No")? \033[1;37;40m\n')

    problem_channel, sub_z, single_indicator = 999, 999, 'None'
    if substack_indicator == 'Yes':
        problem_channel = int(input('\033[2;37;40mWhich channel might that be [1,2...N]? \033[1;37;40m\n'))
        single_indicator = input('\033[2;37;40mDo you want to take a single slice or still project a subset ("Single/Multiple")? \033[1;37;40m\n')
        
        if single_indicator == 'Multiple':
            start_z = int(input('\033[2;37;40mIn that channel, what is the bottom z-slice to include [1,2...N]? \033[1;37;40m\n'))
            end_z = int(input('\033[2;37;40mIn that channel, what is the top Zslice to include [1,2...N]? \033[1;37;40m\n'))
            sub_z = list(range(start_z - 1, end_z))
        elif single_indicator == 'Single':
            single_z = int(input('\033[2;37;40mIn that channel, what is the slice you want to include [1,2...N]? \033[1;37;40m\n'))
            sub_z = single_z - 1
        else:
            print('Choose a valid option, idiot.')
            sys.exit()

    number_worker = input('\033[2;37;40mHow many proteins did you pack into your device (i.e., how many CPUs do you wish to use [e.g., 1, 2, ...N or MusclePower]): \033[1;37;40m\n')
    if number_worker == 'MusclePower':
        print_colored_message('1;34;40', 'Arnie would be proud. Bullets and Peperoni it is.\n')
    else:
        print_colored_message('1;34;40', 'The answer to "Mann oder Muschi" has definitely been determined. While we will continue, however, please note that the T-800 has been dispatched to eradicate you from the timeline.\n')

    if not os.path.exists(input_path):
        print_colored_message('1;31;40', 'You are a moron. The path does not exist.\n')
        print_colored_message('1;31;40', 'Try again with the correct path.\n')
        sys.exit()
    elif not os.listdir(input_path):
        print_colored_message('1;31;40', 'You are an even bigger moron. There are no files in that directory.\n')
        print_colored_message('1;31;40', 'Try putting it in first.\n')
        sys.exit()
    else:
        print_colored_message('1;33;40', 'For now, we will acknowledge your supremacy and are processing your request. Standby.\n')

    return input_path, output_path, median_maximum, problem_channel, sub_z, single_indicator, number_worker

if __name__ == "__main__":
    input_path, output_path, median_maximum, problem_channel, sub_z, single_indicator, number_worker = gather_inputs()
    mip_maker = MIPMaker(input_path, output_path, median_maximum, problem_channel, sub_z, single_indicator)
    mip_maker.run(number_worker)
    print_colored_message('1;34;40', 'Subroutine "4" completed.\n')
    print_colored_message('1;32;40', 'Constantin ist ein Bär.\n')