import glob
import os
import numpy as np
from moviepy.editor import ImageSequenceClip
import cv2
import imageio
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


out_folder = "/home/htung/Desktop/BlenderTemp"
prefix = "Sc0002_*.png"

rgbs = []
for file in sorted(glob.glob(os.path.join(out_folder, prefix))):
    rgb = imageio.imread(file)
    rgb = cv2.resize(rgb, dsize=(128, 128))
    rgbs.append(rgb)

gif_name = prefix.replace("*", "").replace("_","")

rgbs = np.stack(rgbs, axis=0)[:,:,:,:3]
create_gif(os.path.join(out_folder, gif_name), rgbs) 