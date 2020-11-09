#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 11:44:33 2019

@author: michellef
"""
import os
import matplotlib.pyplot as plt                                                              
import glob
import numpy as np 
#from PIL import Image
import pydicom
from pathlib import Path
import dicom, dicom.UID
from dicom.dataset import Dataset, FileDataset


def check_dir(output):
    if not os.path.exists(output):
        os.makedirs(output)
    return None

# def directory_check(dir_path):
#     if str(os.getcwd()) != str(dir_path):
#         os.chdir(dir_path)  
#     return None

def find_dirs(dir_path):
    numpys = {}
    for (dirpath, dirnames, filenames) in os.walk(dir_path):
        dirname = str(Path(dirpath).relative_to(dir_path))
        for n in glob.glob("{}/*.npy".format(dirpath), recursive=True):
            new_name = str(Path(os.path.basename(n)).with_suffix(''))
            numpys[n] = {'Dir': dirname,'Name': new_name}
    return numpys

def load_data(dir_path, output):
    numpys = find_dirs(dir_path)
    for k,v in numpys.items():
        np_pixels = np.load(k)
        save_dir = os.path.join(str(output), str(v['Dir']))
        check_dir(save_dir)
        plt.imshow(np_pixels[:,:,0])
        plt.savefig(os.path.join(save_dir, str(v['Name'] + '.png')))

        
def main():
    dir_path = Path('/homes/michellef/Amyloid/data_michelle')
    output = Path('/homes/michellef/Amyloid/IMAGES')
    load_data(dir_path, output)

    

if __name__ == '__main__':
    main()
    