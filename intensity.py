import numpy as np
import os
import imageio
from pathlib import Path
import time
import pandas as pd
import itk

import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)



from deformationcytometer.includes.includes import getInputFile, getConfig, getFlatfield
from skimage.draw import ellipse








video= getInputFile()


print("video", video)


name_ex = os.path.basename(video)
filename_base, file_extension = os.path.splitext(name_ex)
output_path = os.path.dirname(video)
flatfield = output_path + r'/' + filename_base + '.npy'
configfile = output_path + r'/' + filename_base[:-2] + 'B_config.txt'
results_file = output_path + r'/' + filename_base[:-2] + 'B_evaluated_new.csv'

###for blood cells
#configfile = output_path + r'/' + filename_base + '_config.txt'
#results_file = output_path + r'/' + filename_base + '_evaluated_new.csv'


#%%
config = getConfig(configfile)



batch_size = 100
print(video)
vidcap = imageio.get_reader(video)

cells = []


pixelsize = 0.3176 * 1.0

data = pd.read_csv(results_file)
frames_with_cells = data.frames
frames_with_cells_x = data.x
frames_with_cells_y = data.y
frames_with_cells_irregularity = data.irregularity
frames_with_cells_solidity = data.solidity
frames_with_cells_sharpness = data.sharpness
long_ax = data.long_axis
short_ax = data.short_axis
angles = data.angle
sum_frames = 0
num_frames = 0
#num_frames_old =1

for image_index in frames_with_cells:
    imageindex = int(image_index)
    im = vidcap.get_data(imageindex)
    num_frames = num_frames +1
    im_np = np.array(im, dtype = np.float32)
    sum_frames = sum_frames +im_np
print(num_frames)



flatfield_correction = sum_frames/ num_frames
flatfield_correction = flatfield_correction/np.mean(flatfield_correction)


index =0
def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide( a, b )
        c[ ~ np.isfinite( c )] = 0  # -inf inf NaN
    return c
for image_index in frames_with_cells:  # loops through frames with cells
    imageindex = int(image_index)
    imm = vidcap.get_data(imageindex)

    im_corrected = imm/flatfield_correction

    xvalue = float(frames_with_cells_x[index])
    #print(xvalue)
    yvalue = float(frames_with_cells_y[index])
    Lax = float(long_ax[index])
    Sax = float(short_ax[index])
    angle = float(angles[index])



#ellipse mask of cell
    rr, cc = ellipse(yvalue, xvalue, Sax/pixelsize / 2, Lax / pixelsize / 2, rotation= - angle * np.pi / 180)
    mask = np.zeros((540, 720))
    mask[rr,cc] = 255

    #fig, ax = plt.subplots(2)
    #ax[0].imshow(im_corrected*mask)
    #ax[1].imshow(im_corrected)
    #plt.show()

    mean_intensity = np.mean(im_corrected[mask == 255])
    integral = np.sum(im_corrected[mask==255])
    maximum = np.max(im_corrected[mask==255])
    percent90 = np.percentile((im_corrected[mask==255]), 90)
    std = np.std((im_corrected[mask==255]))

    if index == 0:
        d = {'mean_intensity': [mean_intensity]}
        e = {'integral_intensity': [integral]}
        f = {'max_intensity': [maximum]}
        g = {'percent90_intensity': [percent90]}
        h = {'std_intensity': [std]}
        intensity = pd.DataFrame(data=d)
        integ = pd.DataFrame(data = e)
        maxi = pd.DataFrame(data=f)
        perc = pd.DataFrame(data=g)
        st = pd.DataFrame(data=h)

        #intensity = pd.DataFrame([mean_intensity], columns=list('a'))
        #print(intensity)

    else:
        d = {'mean_intensity': [mean_intensity]}
        e = {'integral_intensity': [integral]}
        f = {'max_intensity': [maximum]}
        g = {'percent90_intensity': [percent90]}
        h = {'std_intensity': [std]}
        append = pd.DataFrame(data = d)
        append1 = pd.DataFrame(data=e)
        append2 = pd.DataFrame(data=f)
        append3 = pd.DataFrame(data=g)
        append4 = pd.DataFrame(data=h)
        intensity = intensity.append(append, ignore_index=True)
        integ = integ.append(append1,  ignore_index=True)
        maxi = maxi.append(append2, ignore_index=True)
        perc = perc.append(append3, ignore_index=True)
        st = st.append(append4, ignore_index=True)
        #print(intensity)
    index += 1


    # Save result:
new_data = data.assign(mean_intensity=intensity, integral_intensity=integ, max_intensity=maxi , percent90_intensity= perc, std_intensity=st )
print(new_data)
result_file = output_path + '/' + filename_base + '_result_intensity.csv'
new_data.to_csv(result_file)

