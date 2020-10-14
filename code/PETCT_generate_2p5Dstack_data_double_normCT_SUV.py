import numpy as np
import os.path
import argparse
import os
import nibabel as nib
import glob
import matplotlib.pyplot as plt
import pyminc.volumes.factory as pyminc
import pandas as pd
from math import log, exp
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # DISABLE CPU WARNING

_ct_name = "ct_normalized_spatiallynormalized_128x128x128.nii.gz"
_highdose_name = "full_default_spatiallynormalized_128x128x128.nii.gz"
_lowdose_name = "reduced_default_spatiallynormalized_128x128x128.nii.gz"
dims_inplane = 128

_dat_name = "dat_50MBq_suv_ptweight_ctnorm_128x128.npy"
_res_name = "res_50MBq_suv_ptweight_128x128.npy"

_csv = 'data_overview_petct.csv'
_csv2 = 'pe2i_nn_patientmeta.csv'

def save_nii(i):
    if not os.path.exists(f'{i}/{_dat_name}'):
        return
    dat = np.memmap(f'{i}/{_dat_name}',dtype='double',mode='r').reshape(128,128,128,2)
    res = np.memmap(f'{i}/{_res_name}',dtype='double',mode='r').reshape(128,128,128)
    ld = dat[...,0].reshape(128,128,128)
    hd = res+ld 
    img = nib.load(f'{i}/{_highdose_name}')
    ld_suv = nib.Nifti1Image(ld, img.affine, img.header)
    nib.save(ld_suv,f'{i}/Lowdose_SUV_50MBq.nii.gz')
    hd_suv = nib.Nifti1Image(hd, img.affine, img.header)
    nib.save(hd_suv,f'{i}/Fulldose_SUV.nii.gz')

def get_feature_patches(pt,reduced_dose,reduced_lowdose_dose,weight=80,verbose=False,getCT=False,folder='train'):

    # Load input
    _lowdose = nib.load(os.path.join(pt,_lowdose_name))
    _ct = nib.load(os.path.join(pt,_ct_name))
    lowdose = np.array(_lowdose.get_fdata(),dtype='double')
    ct = np.array(_ct.get_fdata(),dtype='double')
    lowdose[np.where(lowdose<0)] = 0
    ct = ct
    ct[np.where(ct<-1024)] = -1024
       
    #scale CT
    ct = (ct + 1024) / float(1024+300) # not clamping values over 1!

    # Load reference highdose
    _highdose = nib.load(os.path.join(pt,_highdose_name))
    highdose = np.array(_highdose.get_fdata(),dtype='double')
    highdose[np.where(highdose<0)] = 0
    
    # Scale to SUV
    lowdose_SUV = (lowdose * weight) / float(reduced_lowdose_dose * 1000)
    highdose_SUV = (highdose * weight) / float(reduced_dose * 1000)

    # Compute residual image
    residual = highdose_SUV - lowdose_SUV
    
    dat = np.empty((lowdose_SUV.shape[0],lowdose_SUV.shape[1],lowdose_SUV.shape[2],2))
    dat[...,0] = lowdose_SUV
    dat[...,1] = ct
    
    # Save the 2.5D patches and residual reference
    if not os.path.exists(pt+'/'+_dat_name):
        
        memmap_dat = np.memmap(pt+'/'+_dat_name, dtype='double', mode='w+', shape=dat.shape)
        memmap_dat[:] = dat[:]
        
        del memmap_dat
        
    if not os.path.exists(pt+'/'+_res_name):
        
        memmap_res = np.memmap(pt+'/'+_res_name, dtype='double', mode='w+', shape=(residual.shape))
        memmap_res[:] = residual[:]
        
        del memmap_res

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract data patches in 2.5D.')
    parser.add_argument("--input", help="Specify the input patients used for training (file) or prediction (comma separated if more than one).", type=str)
    parser.add_argument("-v","--verbose", help="Print out verbose information", action="store_true")
    args = parser.parse_args()
    
    csv = pd.read_csv(_csv)
    csv2 = pd.read_csv(_csv2)
    
    for f in os.listdir(args.input):
        if f.startswith('.'):
            #skip1+=1
            continue
        if os.path.exists(os.path.join(args.input,f,_highdose_name)):
            
            # Check CSV
            info = csv[ csv['Patient ID'] == f ].iloc[0]
            dose = int(info['Injected Mbq'])
            diff = float(info['Time difference (minutes)'])
            if dose < 350 or diff < 20 or diff > 60:
                continue
            
            # from CSV2
            weight = int(csv2.query(f'PatientID == "{f}"').PatientWeight)
            assert int(csv2.query(f'PatientID == "{f}"').RadionuclideTotalDose/1000000) == dose            
            
            halflife = 20.38
            reduced_dose = dose*exp(log(2)/halflife*-diff)
            reduced_lowdose_dose = 50*exp(log(2)/halflife*-diff)
            
            
            print("Extracting: %s" % (os.path.join(args.input,f).split('/')[-1]),dose,reduced_dose,reduced_lowdose_dose,diff,weight)
            #get_feature_patches(os.path.join(args.input,f),reduced_dose,reduced_lowdose_dose,weight=weight,verbose=args.verbose)
            save_nii(os.path.join(args.input,f))
