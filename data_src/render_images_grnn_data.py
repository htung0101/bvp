#bvp_path = "/home/htung/Documents/2020/Fall/bvp/bvp"

#import sys
#print(sys.version_info)
#sys.path.append(bvp_path)

#import numpy as np
import bvp
import os
import argparse
import glob
import copy
import numpy as np
#import imageio
#import cv2
#import scipy.misc
from pathlib import Path
#import bpy
#bpy.context.scene.render.engine = 'CYCLES'
import json
#from moviepy.editor import ImageSequenceClip
from imageio_ffmpeg import write_frames
#from scipy.spatial.transform import Rotation as R
import sys
sys.path.append(os.environ['BVP_SOURCE_DIR'])

import bvp_utils
import ipdb
st=ipdb.set_trace
#from bvp.Classes.Camera import Camera
#from bvp.Classes.Scene import Scene

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

def rot2d(theta, vector):
    theta = np.radians(theta)
    r = np.array(( (np.cos(theta), -np.sin(theta)),
               (np.sin(theta),  np.cos(theta)) ))
    return r.dot(vector)

if __name__ == "__main__":
    #import sys
    #print(sys.argv)
    parser = bvp_utils.utils.ArgumentParserForBlender()
    parser.add_argument("-json_file", type=str, default="")
    parser.add_argument("-P", type=str, default="")
    args = parser.parse_args()

    mark_data_dir = bvp_utils.utils.get_markdata_dir()
    with open(os.path.join(mark_data_dir, args.json_file)) as f:
      data = json.load(f)


    #with open('bvp_ses1_trn1_torender.json') as f:
    #  data2 = json.load(f)

    RO = bvp.RenderOptions()
    RO.resolution_x = RO.resolution_y = 256
    RO.BVPopts["Type"] = "all"

    for data_id in range(0, 1):
        scene_data0 = data[data_id]
        #scene_data = data2[data_id]



        dbi = bvp.config
        scene_data0["background"]["dbi"] = dbi
        if scene_data0["sky"] is None:
            scene_data0["sky"] = {}


        scene_data0["sky"]["dbi"] = dbi
        if "override" in scene_data0["sky"]:
            del scene_data0["sky"]["override"]
        Sky = bvp.Sky(**scene_data0["sky"])
        if scene_data0["shadow"] is None:
            scene_data0["shadow"] = {}
        scene_data0["shadow"]["dbi"] = dbi

        print("========== camera =====")
        print(scene_data0["camera"])
        print("======================")

        # compute dist, elevation from the current pos
        init_location = np.array(scene_data0["camera"]["location"][0])
        init_fix_location = np.array(scene_data0["camera"]["fix_location"][0])



        cam_to_lookat = init_location - init_fix_location
        # make init_fix_location closer to the camera
        init_fix_location[:2] = cam_to_lookat[:2]*0.6  + init_fix_location[:2]
        cam_to_lookat = init_location - init_fix_location
        
        new_cam_locs = [init_location]

        for degree in range(20, 360, 20):
            cam_to_lookat_xy = cam_to_lookat[:2]
            rot10 = rot2d(degree, cam_to_lookat_xy)
            new_cam_to_lookat = copy.deepcopy(cam_to_lookat)

            new_cam_to_lookat[:2] = rot10

            
            new_location = init_fix_location + new_cam_to_lookat
            new_cam_locs.append(new_location)

        #st()
        ncam_loc = len(new_cam_locs)

        #dist = np.linalg.norm(cam_to_lookat)
        #print(data_id, "distance", dist)
        #continue
        #st()
        scene_data0["camera"]["location"] = [new_location.tolist() for new_location in new_cam_locs]
        scene_data0["camera"]["fix_location"] = [init_fix_location.tolist()] * ncam_loc 
        scene_data0["camera"]["frames"] = [x for x in range(1, ncam_loc + 1)]
        scene_data0["frame_range"] = [1, ncam_loc]

        #st()

        Cam = bvp.Camera(**scene_data0["camera"])
        Shadow = bvp.Shadow(**scene_data0["shadow"])

        Objects = []
        for obj_arg in scene_data0["objects"]:
            obj_arg["dbi"] = dbi
            Object = bvp.Object(**obj_arg)
            Objects.append(Object)

        BG = bvp.Background(**scene_data0["background"])
        #nCamLoc=5

        ScnL = []
        frames = (1,1)


        #import ipdb; ipdb.set_trace()
        Scn = bvp.Scene(camera=Cam, background=BG, sky=Sky, objects=Objects, shadow=Shadow, frame_range=scene_data0["frame_range"], fname=scene_data0["render_path"], frame_rate=scene_data0["frame_rate"])
        Scn.create(RO)
        Scn.render(RO)

        # out_folder = os.path.expanduser(dbi.get("path", "render_dir"))
        # file_prefix = scene_data0["render_path"].replace("##", "*")+ ".png"
        # rgbs = []
        # gif_name = os.path.join(os.path.expanduser(dbi.get("path", "render_dir")), scene_data0["render_path"].replace("#", "")[:-1] + ".gif")

        # writer = write_frames(gif_name, (256, 256))
        # import ipdb; ipdb.set_trace()

        # for img_file in Path(out_folder).glob(file_prefix):
        #     print(img_file)
        #     rgb = scipy.misc.imread(img_file).astype(np.uint8)
        #     rgb = bytes(rgb)
        #     import ipdb; ipdb.set_trace()
        #     #rgb = cv2.resize(rgb, dsize=(128, 128))
        #     writer.send(rgb)

        #     #rgbs.append(rgb)
        # print("video in ", gif_name)
        # writer.close()
        
        #create_gif(os.path.join(dbi.get("path", "render_dir"), gif_name), rgbs)

        Scn.clear()


    print("end")

#ScnL.append(Scn)
#SL = bvp.SceneList(ScnList=ScnL, RenderOptions=RO)
#SL.RenderSlurm(RenderGroupSize=nCamLoc)