import glob
import os
import argparse
import click
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


#out_folder = "/home/htung/Desktop/BlenderTemp"
#prefix = "Sc0002_*.png"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="/home/htung/Desktop/BlenderTemp")
    parser.add_argument("--prefix", type=str, default="Sc0001_*.png")
    parser.add_argument("--out_dir", type=str, default="/home/htung/Desktop/BlenderTemp")
    parser.add_argument("--outfile_prefix", type=str, default="test1_")
    args = parser.parse_args()

     
    # read all rgbs
    rgbs = []
    for file in sorted(glob.glob(os.path.join(args.data_dir, args.prefix))):
        rgb = imageio.imread(file)
        rgb = cv2.resize(rgb, dsize=(128, 128))
        rgbs.append(rgb)

    gif_name = args.prefix.replace("*", "").replace("_","")
    if args.outfile_prefix is not "":
        gif_name = args.outfile_prefix + gif_name

    rgbs = np.stack(rgbs, axis=0)[:,:,:,:3]
    create_gif(os.path.join(args.out_dir, gif_name), rgbs) 