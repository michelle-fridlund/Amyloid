#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 14:05:49 2020

@author: michellef
"""
import os
import matplotlib.pyplot as plt
import numpy as np



def load_data(my_np):
    my_ims = np.load(my_np)
    return im_conv = np.stack(my_ims, axis=2).astype("uint8")

def get_image(my_np):
    my_np = load_data(my_np)
    return plt.imshow(my_np[:,:,0])

file = '/homes/michellef/Amyloid/data_michelle/adaxmvprdo/Fulldose_SUV.npy'

get_image(file)

