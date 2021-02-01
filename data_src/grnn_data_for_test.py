#bvp_path = "/home/htung/Documents/2020/Fall/bvp/bvp"

#import sys
#print(sys.version_info)
#sys.path.append(bvp_path)

#import numpy as np
import bpy
import bvp
import h5py
import os
import argparse
import glob
import copy
import numpy as np
#import imageio
#import cv2
import scipy.misc
from pathlib import Path
from PIL import Image
#import bpy
#bpy.context.scene.render.engine = 'CYCLES'
import json
#from moviepy.editor import ImageSequenceClip
from imageio_ffmpeg import write_frames
#from scipy.spatial.transform import Rotation as R
import sys
sys.path.append(os.environ["BVP_SOURCE_DIR"])
import bvp_utils.utils
import bvp_utils.io

import ipdb
st=ipdb.set_trace
#from bvp.Classes.Camera import Camera
#from bvp.Classes.Scene import Scene

def get_sensor_size(sensor_fit, sensor_x, sensor_y):
    if sensor_fit == 'VERTICAL':
        return sensor_y
    return sensor_x

def get_sensor_fit(sensor_fit, size_x, size_y):
    if sensor_fit == 'AUTO':
        if size_x >= size_y:
            return 'HORIZONTAL'
        else:
            return 'VERTICAL'
    return sensor_fit

def get_calibration_matrix_K_from_blender(camd):
    if camd.type != 'PERSP':
        raise ValueError('Non-perspective cameras not supported')
    scene = bpy.context.scene
    f_in_mm = camd.lens
    scale = scene.render.resolution_percentage / 100
    resolution_x_in_px = scale * scene.render.resolution_x
    resolution_y_in_px = scale * scene.render.resolution_y
    sensor_size_in_mm = get_sensor_size(camd.sensor_fit, camd.sensor_width, camd.sensor_height)
    sensor_fit = get_sensor_fit(
        camd.sensor_fit,
        scene.render.pixel_aspect_x * resolution_x_in_px,
        scene.render.pixel_aspect_y * resolution_y_in_px
    )
    pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
    if sensor_fit == 'HORIZONTAL':
        view_fac_in_px = resolution_x_in_px
    else:
        view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px
    pixel_size_mm_per_px = sensor_size_in_mm / f_in_mm / view_fac_in_px
    s_u = 1 / pixel_size_mm_per_px
    s_v = 1 / pixel_size_mm_per_px / pixel_aspect_ratio

    # Parameters of intrinsic calibration matrix K
    u_0 = resolution_x_in_px / 2 - camd.shift_x * view_fac_in_px
    v_0 = resolution_y_in_px / 2 + camd.shift_y * view_fac_in_px / pixel_aspect_ratio
    skew = 0 # only use rectangular pixels

    K = np.array(
        [[s_u, skew, u_0],
         [  0,  s_v, v_0],
         [  0,    0,   1]])
    return K



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


jsonfile_to_id = {"bvp_ses1_trn1.json": "0",
                  "bvp_ses1_trn2.json": "1",
                  "bvp_ses1_trn3.json": "2",
                  "bvp_ses1_trn4.json": "3",
                  "bvp_ses1_val.json": "val"
                  }

id_to_depthfile = {"0": "bvp_dist/distance_ses00_trn_p000_2fce59d838774e989f4427b60447b568.hdf",
                   "1": "bvp_dist/distance_ses00_trn_p001_2fce59d838774e989f4427b60447b568.hdf",
                   "2": "bvp_dist/distance_ses00_trn_p002_2fce59d838774e989f4427b60447b568.hdf",
                   "3": "bvp_dist/distance_ses00_trn_p003_2fce59d838774e989f4427b60447b568.hdf",
                   "val": "bvp_dist/distance_ses00_val_p000_a090392cfe0a42f8b0983fefc15d0840.hdf"}
id_to_rgbfolder = {"0": "berkeley_box/stimuli_trn_run0",
                   "1": "berkeley_box/stimuli_trn_run1",
                   "2": "berkeley_box/stimuli_trn_run2",
                   "3": "berkeley_box/stimuli_trn_run3",
                   "val": "berkeley_box/stimuli_val",
                  }

id_to_imgstart = {"0": 0,
                  "1": 9000,
                  "2": 18000,
                  "3": 27000,
                  "val": 0}

if __name__ == "__main__":
    #import sys
    #print(sys.argv)
    parser = bvp_utils.utils.ArgumentParserForBlender()
    parser.add_argument("-json_file", type=str, default="")
    parser.add_argument("-scene_id", type=int)
    parser.add_argument("-output_dir", type=str, default="/home/htung/Desktop/BlenderTemp/")
    parser.add_argument("-data_dir", type=str, default="/media/htung/Extreme SSD/fish/mark_data/")
    args = parser.parse_args()

    mark_data_dir = bvp_utils.utils.get_markdata_dir()
    print(mark_data_dir)
    with open(os.path.join(mark_data_dir, args.json_file)) as f:
      data = json.load(f)

    file_id  = jsonfile_to_id[args.json_file]
    depth_file = id_to_depthfile[file_id]
    rgb_folder = id_to_rgbfolder[file_id]
    img_startid = id_to_imgstart[file_id]
    
    #with open('bvp_ses1_trn1_torender.json') as f:
    #  data2 = json.load(f)

    output_dir = args.output_dir

    RO = bvp.RenderOptions()
    RO.resolution_x = RO.resolution_y = 128
    RO.BVPopts["Type"] = "all"
    RO.BVPopts["Zdepth"] = True
    RO.BVPopts["BasePath"] = os.path.join(output_dir, "Scenes/{scene_name}")

    #RO.BVPopts["Normal"] = "True"
    #RO.image_settings = {'color_depth': 32, 'file_format': 'PNG'}

    # find the starting point for this frame
    correction = dict()#{0: 47, }
    start_frame_id = 0
    cum_frames = 0
    for scene_id in range(args.scene_id):
        #print(scene_id, start_frame_id)
        if scene_id in correction:
            n_frames = correction[scene_id]
        else:
            n_frames = int(data[scene_id]["camera"]["frames"][1])
        
        if scene_id>1 and (scene_id)%10 == 0:
            print(scene_id, start_frame_id)
            print("    %s" %(str(cum_frames)))
            cum_frames = 0
        cum_frames += n_frames
        start_frame_id += n_frames
    st()

    for data_id in range(args.scene_id, args.scene_id + 1):
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


        # compute dist, elevation from the current pos
        init_location = np.array(scene_data0["camera"]["location"][0])
        init_fix_location = np.array(scene_data0["camera"]["fix_location"][0])



        cam_to_lookat = init_location - init_fix_location
        
        ncam_loc = int(scene_data0["camera"]["frames"][1])
        start_pos = init_location
        end_pos = init_location = np.array(scene_data0["camera"]["location"][1])
        end_fix_location = np.array(scene_data0["camera"]["fix_location"][1])

        new_cam_locs = [start_pos * (1-x) + x * end_pos for x in np.linspace(0, 1, num=ncam_loc)]
        new_fix_locs = [init_fix_location * (1-x) + x * end_fix_location for x in np.linspace(0, 1, num=ncam_loc)]



        scene_data0["camera"]["location"] = [new_location.tolist() for new_location in new_cam_locs]
        scene_data0["camera"]["fix_location"] = [new_fix.tolist() for new_fix in new_fix_locs] 
        scene_data0["camera"]["frames"] = [x for x in range(1, ncam_loc + 1)]
        scene_data0["frame_range"] = [1, ncam_loc]

        Cam = bvp.Camera(**scene_data0["camera"])
        Shadow = bvp.Shadow(**scene_data0["shadow"])
        for o in bpy.data.objects:
            if o.name == "Cube":
                o.select = True
            else:
                o.select = False
        bpy.ops.object.delete()

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

        depth_camXs = []
        rgb_camXs = []
        frame_id = start_frame_id
        depth_filename = os.path.join(args.data_dir, depth_file)
        depth_data = h5py.File(depth_filename)["data"]

        for cam_id in range(ncam_loc):
            Scn.place_camera(cam_id)
            #KK = Cam.get_intrinsics(Scn)
            #filepath = Scn.set_scene(RO, frame_id=cam_id)
            filepath = Scn.render_frame_by_frame(RO, frame_id=cam_id)
            rgb_filename = os.path.join(args.data_dir, rgb_folder, "fr%s.png" %(str(img_startid + frame_id + cam_id).zfill(7)))
            depth_filename = filepath.replace("Scenes", "Zdepth") + "_z0001.exr"
            #st()
            # read depth image
            depth_cam = bvp_utils.io.exr_to_array(depth_filename)
            depth_camXs.append(depth_cam[:,:,0])

            rgb_arr = np.array(Image.open(rgb_filename).resize((128, 128)))
            rgb_camXs.append(rgb_arr[:,:,:3])
        
        #depth_camXs = depth_data[start_frame_id:start_frame_id + ncam_loc]


        world_T_fix = np.eye(4)
        world_T_fix[:3, 3] = init_fix_location


        pix_T_cams = []
        camR_T_camXs = []
        for cam_id in range(ncam_loc):
            #print("======== camera %s ========" %(str(cam_id)))
            world_T_cam = bpy.data.objects["cam_camera000." + str(cam_id + 1).zfill(3)].matrix_world
            world_T_cam = np.array([list(row) for row in world_T_cam])
            fix_T_cam = np.matmul(np.linalg.inv(world_T_fix), world_T_cam)
            pix_T_cam = get_calibration_matrix_K_from_blender(bpy.data.cameras['cam_camera000.' + str(cam_id + 1).zfill(3)])
            pix_T_cams.append(pix_T_cam)
            camR_T_camXs.append(fix_T_cam)

        save_dict = dict()
        save_dict["pix_T_cams"] = np.stack(pix_T_cams, axis=0)
        save_dict["camR_T_camXs"] = np.stack(camR_T_camXs, axis=0)
        save_dict["depth_camXs"] = np.stack(depth_camXs, axis=0)
        save_dict["rgb_camXs"] = np.stack(rgb_camXs, axis=0)

        scene_name = Scn.fname

        vis_save_path = os.path.join(output_dir, "visual_data_%s.npy" %(scene_name))
        np.save(vis_save_path, save_dict)


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