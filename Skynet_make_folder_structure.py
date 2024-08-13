# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:37:33 2024

@author: b.kramer
"""


import os

os.system('color')

# Welcome Message
print('')
print('\033[1;34;40mYou accessed subroutine "22": The standard analysis folder with all subdirectories. \033[1;37;40m \n')

# Location of mask images to process
print('')
input_path = input('\033[2;37;40mPlease provide the location in which you want to create all the subfolders: \033[1;37;40m \n')
# Location of csv files to process

if not os.path.exists(input_path):
        os.mkdir(input_path)

# go alphabetically

# Analysis
analysis_path = '/'.join([input_path,'ANALYSIS'])
code_path = '/'.join([analysis_path,'CODE'])
figure_path = '/'.join([analysis_path,'FIGURES'])
figure_path_raw = '/'.join([figure_path,'RAW'])
figure_path_processed = '/'.join([figure_path,'PROCESSED'])

if not os.path.exists(analysis_path):
        os.mkdir(analysis_path)
        
if not os.path.exists(code_path):
        os.mkdir(code_path)

if not os.path.exists(figure_path):
        os.mkdir(figure_path)
        
if not os.path.exists(figure_path_raw):
        os.mkdir(figure_path_raw)
        
if not os.path.exists(figure_path_processed):
        os.mkdir(figure_path_processed)

# Assembly
assembly_path = '/'.join([input_path,'ASSEMBLY'])
csv_path = '/'.join([assembly_path,'CSV'])
masks_path = '/'.join([assembly_path,'MASKS'])
data_output_path = '/'.join([assembly_path,'OUTPUT'])

if not os.path.exists(assembly_path):
        os.mkdir(assembly_path)
        
if not os.path.exists(csv_path):
        os.mkdir(csv_path)

if not os.path.exists(masks_path):
        os.mkdir(masks_path)
        
if not os.path.exists(data_output_path):
        os.mkdir(data_output_path)


# cellpose
cellpose_path = '/'.join([input_path,'CELLPOSE'])
cellpose_exploration_path = '/'.join([cellpose_path,'EXPLORATION'])
cellpose_segmentation_path = '/'.join([cellpose_path,'SEGMENTATION'])

cellpose_subset_path = '/'.join([cellpose_exploration_path,'IMAGESUBSET'])
cellpose_exp_segmentation_path = '/'.join([cellpose_exploration_path,'SEGMENTATION'])
cellpose_exp_nucleus_path = '/'.join([cellpose_exp_segmentation_path,'NUCLEUS'])
cellpose_exp_cell_path = '/'.join([cellpose_exp_segmentation_path,'CELL'])
cellpose_exp_covered_path = '/'.join([cellpose_exp_segmentation_path,'COVERED'])

cellpose_seg_nucleus_path = '/'.join([cellpose_segmentation_path,'NUCLEUS'])
cellpose_seg_cell_path = '/'.join([cellpose_segmentation_path,'CELL'])
cellpose_seg_covered_path = '/'.join([cellpose_segmentation_path,'COVERED'])


if not os.path.exists(cellpose_path):
        os.mkdir(cellpose_path)
        
if not os.path.exists(cellpose_exploration_path):
        os.mkdir(cellpose_exploration_path)

if not os.path.exists(cellpose_segmentation_path):
        os.mkdir(cellpose_segmentation_path)
        

if not os.path.exists(cellpose_subset_path):
        os.mkdir(cellpose_subset_path)
        
if not os.path.exists(cellpose_exp_segmentation_path):
        os.mkdir(cellpose_exp_segmentation_path)

if not os.path.exists(cellpose_exp_nucleus_path):
        os.mkdir(cellpose_exp_nucleus_path)

if not os.path.exists(cellpose_exp_cell_path):
        os.mkdir(cellpose_exp_cell_path)
        
if not os.path.exists(cellpose_exp_covered_path):
        os.mkdir(cellpose_exp_covered_path)
   

if not os.path.exists(cellpose_seg_nucleus_path):
        os.mkdir(cellpose_seg_nucleus_path)
        
if not os.path.exists(cellpose_seg_cell_path):
        os.mkdir(cellpose_seg_cell_path)

if not os.path.exists(cellpose_seg_covered_path):
        os.mkdir(cellpose_seg_covered_path)
        

# cellprofiler
cellprofiler_path = '/'.join([input_path,'CELLPROFILER'])
cellprofiler_exploration_path = '/'.join([cellprofiler_path,'EXPLORATION'])

cellprofiler_exp_subset_path = '/'.join([cellprofiler_exploration_path,'IMAGESUBSET'])
cellprofiler_exp_segmentation_path = '/'.join([cellprofiler_exploration_path,'SEGMENTATION'])
cellprofiler_exp_quantification_path = '/'.join([cellprofiler_exploration_path,'QUANTIFICATION'])

cellprofiler_pipeline_path = '/'.join([cellprofiler_path,'PIPELINE'])
cellprofiler_quantification_path = '/'.join([cellprofiler_path,'QUANTIFICATION'])
cellprofiler_quantification_ind_path = '/'.join([cellprofiler_path,'QUANTIFICATION_INDIVIDUAL'])
cellprofiler_segmentation_path = '/'.join([cellprofiler_path,'SEGMENTATION'])
cellprofiler_segmentation_ind_path = '/'.join([cellprofiler_path,'SEGMENTATION_ind'])


if not os.path.exists(cellprofiler_path):
        os.mkdir(cellprofiler_path)
        
if not os.path.exists(cellprofiler_exploration_path):
        os.mkdir(cellprofiler_exploration_path)

      

if not os.path.exists(cellprofiler_exp_subset_path):
        os.mkdir(cellprofiler_exp_subset_path)
        
if not os.path.exists(cellprofiler_exp_segmentation_path):
        os.mkdir(cellprofiler_exp_segmentation_path)

if not os.path.exists(cellprofiler_exp_quantification_path):
        os.mkdir(cellprofiler_exp_quantification_path)



if not os.path.exists(cellprofiler_pipeline_path):
        os.mkdir(cellprofiler_pipeline_path)
        
if not os.path.exists(cellprofiler_quantification_path):
        os.mkdir(cellprofiler_quantification_path)
   
if not os.path.exists(cellprofiler_quantification_ind_path):
        os.mkdir(cellprofiler_quantification_ind_path)
        
if not os.path.exists(cellprofiler_segmentation_path):
        os.mkdir(cellprofiler_segmentation_path)

if not os.path.exists(cellprofiler_segmentation_ind_path):
        os.mkdir(cellprofiler_segmentation_ind_path)
        
# data
data_path = '/'.join([input_path,'DATA'])

if not os.path.exists(data_path):
        os.mkdir(data_path)
        
# flatfield
flatfield_path = '/'.join([input_path,'FLATFIELD'])

flatfield_corr_path = '/'.join([flatfield_path,'CORRECTION'])
flatfield_processed_path = '/'.join([flatfield_path,'PROCESSED'])
flatfield_raw_path = '/'.join([flatfield_path,'RAW'])


if not os.path.exists(flatfield_path):
        os.mkdir(flatfield_path)
   
if not os.path.exists(flatfield_corr_path):
        os.mkdir(flatfield_corr_path)
        
if not os.path.exists(flatfield_processed_path):
        os.mkdir(flatfield_processed_path)

if not os.path.exists(flatfield_raw_path):
        os.mkdir(flatfield_raw_path)
        
# illcorr
illcorr_path = '/'.join([input_path,'ILCORR'])

if not os.path.exists(illcorr_path):
        os.mkdir(illcorr_path)
        
# illcorr_2
illcorr_2_path = '/'.join([input_path,'ILCORR_2'])

if not os.path.exists(illcorr_2_path):
        os.mkdir(illcorr_2_path)
        
# metadata
metadata_path = '/'.join([input_path,'METADATA'])

if not os.path.exists(metadata_path):
        os.mkdir(metadata_path)
        
# MIP
mip_path = '/'.join([input_path,'MIP'])

if not os.path.exists(mip_path):
        os.mkdir(mip_path)
        
# NIS
nis_path = '/'.join([input_path,'NIS'])

if not os.path.exists(nis_path):
        os.mkdir(nis_path)
        
# TIFF
nis_path = '/'.join([input_path,'TIFF'])

if not os.path.exists(nis_path):
        os.mkdir(nis_path)
        
# PNG
png_path = '/'.join([input_path,'PNG'])

if not os.path.exists(png_path):
        os.mkdir(png_path)
        

# spotdetection
spotdetection_path = '/'.join([input_path,'SPOTDETECTION'])

spotdetection_subset_path = '/'.join([spotdetection_path,'IMAGESUBSET'])
spotdetection_quantification_path = '/'.join([spotdetection_path,'QUANTIFICATION'])
spotdetection_segmentation_path = '/'.join([spotdetection_path,'SEGMENTATION'])
spotdetection_spotimages_path = '/'.join([spotdetection_path,'SPOTIMAGES'])
spotdetection_temp_path = '/'.join([spotdetection_path,'TEMP'])
spotdetection_thresholds_path = '/'.join([spotdetection_path,'THRESHOLDS'])

if not os.path.exists(spotdetection_path):
        os.mkdir(spotdetection_path)
        

if not os.path.exists(spotdetection_subset_path):
        os.mkdir(spotdetection_subset_path)
        
if not os.path.exists(spotdetection_quantification_path):
        os.mkdir(spotdetection_quantification_path)
        
if not os.path.exists(spotdetection_segmentation_path):
        os.mkdir(spotdetection_segmentation_path)
        
if not os.path.exists(spotdetection_spotimages_path ):
        os.mkdir(spotdetection_spotimages_path )
        
if not os.path.exists(spotdetection_temp_path):
        os.mkdir(spotdetection_temp_path)
        
if not os.path.exists(spotdetection_thresholds_path):
        os.mkdir(spotdetection_thresholds_path)
        
# stitched
stitched_path = '/'.join([input_path,'STITCHED'])

if not os.path.exists(stitched_path):
        os.mkdir(stitched_path)

# Say goodbye
print('\033[1;34;40mSubroutine "22" completed. \033[1;37;40m \n')
print('\033[1;32;40mConstantin ist ein Bär. \033[1;37;40m \n')