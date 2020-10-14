import numpy as np, os, glob, pickle

_res_double_name = "res_10_suv_128x128.npy"
_dat_ctnorm_double_name = "dat_10_suv_ctnorm_128x128.npy"

_res_suv_double_name = "res_50MBq_suv_128x128.npy"
_dat_suv_ctnorm_double_name = "dat_50MBq_suv_ctnorm_128x128.npy"

_res_suv_ptweight_double_name = "res_50MBq_suv_ptweight_128x128.npy"
_dat_suv_ptweight_ctnorm_double_name = "dat_50MBq_suv_ptweight_ctnorm_128x128.npy"

_res_suv_ptweight_double_name = "Lowdose_SUV_50MBq.npy"
_dat_suv_ptweight_ctnorm_double_name ="Fulldose_SUV.npy"

    
def load_stack_suv_ptweight_ctnorm_double(mode,z=None, return_studyid=False, augment=False, orientation='axial'):

    global root, summary

    indices = np.random.randint(0, len(summary[mode]), 1)
    stats = summary[mode][indices[0]]

    # --- Load data and labels 
    fname = '%s/%s/%s' % (root, stats,_dat_suv_ptweight_ctnorm_double_name)
    dat = np.memmap(fname, dtype='double', mode='r')
    dat = dat.reshape(128,128,128,2)

    fname = '%s/%s/%s' % (root, stats,_res_suv_ptweight_double_name)
    res = np.memmap(fname, dtype='double', mode='r')
    res = res.reshape(128,128,128)

    # --- Determine slice
    if z == None:
        z = np.random.randint(8,128-8,1)[0]
    
    if orientation=='axial':
        dat_stack = dat[:,z-8:z+8,:,:]
        res_stack = res[:,z-8:z+8,:]
        dat_stack = np.swapaxes(dat_stack,1,2)
        res_stack = np.swapaxes(res_stack,1,2)
    elif orientation=='coronal':
        dat_stack = dat[:,:,z-8:z+8,:]
        res_stack = res[:,:,z-8:z+8]
    
    if augment:
        # Augment data
        r = np.random.random()
        if r < 0.2:
            dat_stack = np.rot90(dat_stack,1) # rot 90
            res_stack = np.rot90(res_stack,1)
        elif r < 0.4:
            dat_stack = np.rot90(dat_stack,3) # rot -90
            res_stack = np.rot90(res_stack,3)
        elif r < 0.6:
            dat_stack = np.flipud(dat_stack) # flip UD
            res_stack = np.flipud(res_stack)
        elif r < 0.8:
            dat_stack = np.fliplr(dat_stack) # flip LR
            res_stack = np.fliplr(res_stack)
            # normal

    if return_studyid:
        return dat_stack, res_stack, stats
    else:
        return dat_stack, res_stack

def load_all_suv_ptweight_ctnorm_double(mode, ind=None):

    global root, summary

    if ind == None:
        ind = np.random.randint(0, len(summary[mode]), 1)[0]
    else:
        ind = [idx for idx, pt in enumerate(summary[mode]) if pt==ind][0]
    stats = summary[mode][ind]

    # --- Load data and labels 
    fname = '%s/%s/%s' % (root, stats,_dat_suv_ptweight_ctnorm_double_name)
    dat = np.memmap(fname, dtype='double', mode='r')
    dat = dat.reshape(128,128,128,2)

    fname = '%s/%s/%s' % (root, stats,_res_suv_ptweight_double_name)
    res = np.memmap(fname, dtype='double', mode='r')
    res = res.reshape(128,128,128)
    
    return dat, res, stats



def get_summary(mode):
    return summary[mode]

def set_root(loc=None):
    global root, summary

    if loc is None:
        paths = ['PETCT']
        for path in paths:
            if os.path.exists(path):
                loc = path
                break

    #root = loc
    root = '/homes/michellef/Amyloid/data_michelle'
    summary_file = '%s/data_suv.pickle' % root
    summary = pickle.load(open(summary_file, 'rb'))

# --- Set root and summary
global root, summary
set_root()
