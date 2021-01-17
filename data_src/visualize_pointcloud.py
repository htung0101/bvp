import os
import json
import cv2
import numpy as np
import imageio
import open3d as o3d

import ipdb
st=ipdb.set_trace


import sys
sys.path.append(os.environ["BVP_SOURCE_DIR"])
import bvp_utils.utils
quantized_dir = bvp_utils.utils.get_quantized_dir()
sys.path.append(quantized_dir)

import pcp_utils.np_vis

filename = '/home/htung/Desktop/BlenderTemp/visual_data_Sc0003_##.npy'

def visualize(images, bbox_points_from_mesh=None, clip_radius=5.0):
    depths = images['depth_camXs']
    pix_T_cams = images['pix_T_cams']
    #pix_T_cams[:,0,0] = 600
    #pix_T_cams[:,1,1] = 600
    origin_T_camXs = images['camR_T_camXs']

    origin_T_camXs[:,:,1] = origin_T_camXs[:,:,1] * (-1)
    origin_T_camXs[:,:,2] = origin_T_camXs[:,:,2] * (-1)


    _, xyz_camRs, _ = pcp_utils.np_vis.unproject_depth(depths,
        pix_T_cams,
        origin_T_camXs,
        camR_T_origin = None, #np.linalg.inv(self.origin_T_adam),
        clip_radius=clip_radius,
        do_vis=False)


    all_xyz_camR = np.concatenate(xyz_camRs[:], axis=0)
    frame = o3d.geometry.TriangleMesh.create_coordinate_frame(origin=np.zeros(3), size=0.8)
    object_pcd = pcp_utils.np_vis.get_pcd_object(all_xyz_camR, clip_radius=10000.0)
    things_to_print = [object_pcd, frame]
    if bbox_points_from_mesh is not None:
        bbox_lineset_from_mesh = pcp_utils.np_vis.make_lineset(bbox_points_from_mesh)
        things_to_print.append(bbox_lineset_from_mesh)
    # transform object xpos and xmat to the adam coordinate (x right, y downs)
    #bbox_lineset_from_mesh_adam = pcp_utils.np_vis.make_lineset(bbox_points_from_mesh_adam)
    o3d.visualization.draw_geometries(things_to_print) #, bbox_lineset_from_mesh_adam])


data = np.load(filename, allow_pickle=True).item()

visualize(data, clip_radius=2000)


# arr = cv2.imread(filename, cv2.IMREAD_UNCHANGED).astype(np.float32)
# arr[arr > 1000] = 0
# imageio.imwrite("depth.png", arr/np.max(arr))
# pix_T_cams = np.array([])
# origin_T_camXs = np.array([])

st()
 