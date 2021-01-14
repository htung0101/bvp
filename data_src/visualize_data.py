import h5py
import imageio
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from moviepy.editor import ImageSequenceClip

import ipdb
st = ipdb.set_trace

def create_gif(filename, array, fps=10, scale=1.0):
    """creates a gif given a stack of ndarray using moviepy
    Parameters
    ----------
    filename : string
        The filename of the gif to write to
    array : array_like
        A numpy array that contains a sequence of images
    fps : int
        frames per second (default: 10)
    scale : float
        how much to rescale each image by (default: 1.0)
    """
    fname, _ = os.path.splitext(filename)   #split the extension by last period
    filename = fname + '.gif'               #ensure the .gif extension
    if array.ndim == 3:                     #If number of dimensions are 3, 
        array = array[..., np.newaxis] * np.ones(3)   #copy into the color 
                                                      #dimension if images are 
                                                      #black and white
    clip = ImageSequenceClip(list(array), fps=fps).resize(scale)
    clip.write_gif(filename, fps=fps)
    return clip


file_id = "0"
trim_dict={"0": [0, 48, 71, 106, 149, 199, 246, 284, 335, 374, 424, 464, 495, 541, 574, 619, 677, 731, 769]}

filenames = {"0": "bvp_dist/distance_ses00_trn_p000_2fce59d838774e989f4427b60447b568.hdf"}
rgb_folder = {"0": "berkeley_box/stimuli_trn_run0"}


filename = filenames[file_id]
data = h5py.File(filename)["data"]
rgb_path = rgb_folder[file_id]

"""
data: 9000 x 128 x 128
"""
ndepth = data.shape[0]



for trim_id, step_id in enumerate(trim_dict[file_id][:-1]):
    


    next_step_id = trim_dict[file_id][trim_id + 1]
    
    rgbs = []
    for img_id in range(step_id, next_step_id):
        rgb = imageio.imread(os.path.join(rgb_path, f'fr{img_id:07}.png'))
        rgb = cv2.resize(rgb, dsize=(128, 128))
        rgbs.append(rgb)
    
    rgbs = np.stack(rgbs, axis=0)[:,:,:,:3]
    depths = data[step_id:next_step_id]
    depths[depths>80] = 80
    depths = depths*255/80
    depths = np.tile(np.expand_dims(depths, -1).astype(np.uint8), [1,1,1,3])


    create_gif(f'vis/rgbs_{file_id}_step{step_id}.gif', rgbs)  
    create_gif(f'vis/depths_{file_id}_step{step_id}.gif', depths)
    create_gif(f'vis/rgbd_{file_id}_step{step_id}.gif', np.concatenate([rgbs, depths], axis=2))
    #fig = plt.figure()
    #ims = []
    # for image_id in range(next_step_id - step_id):
    #     depth_img = depth[image_id]#np.concatenate([depth[i] for i in range(30)], axis=0)
    #     depth_img[depth_img > 100] = 100
    #     depth_img = depth_img * 255/100
    
    #     im = plt.imshow(depth_img, animated=True)
    # ims.append([im])
    # make a fig from this
    #depth_img = np.concatenate([depth[i] for i in range(next_step_id - step_id)], axis=0)
    #imageio.imwrite("vis/depth.png", depth_img)

    #ani = animation.ArtistAnimation(fig, ims, interval=200, blit=True,
    #                            repeat_delay=2000)

    plt.show()



st()
print("hello")