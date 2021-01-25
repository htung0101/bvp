import os
import json
import cv2
import argparse
import numpy as np
import imageio
import open3d as o3d
import imageio

import ipdb
st=ipdb.set_trace


import sys
sys.path.append(os.environ["BVP_SOURCE_DIR"])
import bvp_utils.utils
quantized_dir = bvp_utils.utils.get_quantized_dir()
sys.path.append(quantized_dir)

import pcp_utils.np_vis



def visualize(images, bbox_points_from_mesh=None, clip_radius=5.0, frame_size=10.0):
    crop_range = [item * 1000 for item in [-1, 1, -1, 1, -1, 1]]

    XMIN, XMAX, YMIN, YMAX, ZMIN, ZMAX = crop_range

    depths = images['depth_camXs']
    pix_T_cams = images['pix_T_cams']
    if depths.shape[1] == 256:

        depths = depths[:,::2, ::2]
        pix_T_cams[:,0,0] *= 0.5
        pix_T_cams[:,1,1] *= 0.5
        pix_T_cams[:,:2,2] *= 0.5

    origin_T_camXs = images['camR_T_camXs']
    H, W = depths[0].shape


    rgb_cat = np.concatenate([x[0] for x in np.split(images["rgb_camXs"], images["rgb_camXs"].shape[0], 0)], axis=1)
    depth_cat = np.concatenate([x[0] for x in np.split(depths, images["rgb_camXs"].shape[0], 0)], axis=1)


    imageio.imsave("rgb.png", rgb_cat)
    imageio.imsave("depth.png", depth_cat)
    

    origin_T_camXs[:,:,1] = origin_T_camXs[:,:,1] * (-1)
    origin_T_camXs[:,:,2] = origin_T_camXs[:,:,2] * (-1)
    # take the first frame and see its range
    depth_at_center = np.median(depths[0])

    # build boundary pixel for this

    boundary_pixel = []

    #for h in range(H):
    h = (H-1)/2
    left_pixel = np.zeros((3))
    left_pixel[1] = h#int(H/2)h
    left_pixel[2] = depth_at_center

    right_pixel = np.zeros((3))
    right_pixel[0] = int(W)
    right_pixel[1] = h #int(H/2)
    right_pixel[2] = depth_at_center
    boundary_pixel.append(left_pixel)
    boundary_pixel.append(right_pixel)

    points = np.stack(boundary_pixel, axis=0)
    bd_pts = pcp_utils.np_vis.unproject_pts(points, pix_T_cams[0], origin_T_camXs[0],
                                 clip_radius=clip_radius)
    center = np.mean(bd_pts, axis=0)
    cam_center = origin_T_camXs[0][:3, 3]

    #center =  np.zeros(3)#origin_T_camXs[0][:3, 3]
    center_to_boundary = np.linalg.norm(center - bd_pts, axis=1)[0] * 2.0
    if frame_size == "auto":
        frame_size = center_to_boundary * 0.2



    boundary_lineset = pcp_utils.np_vis.make_lineset_from_rot(center, center_to_boundary * 2)

    #pix_T_cams[:,0,0] = 600
    #pix_T_cams[:,1,1] = 600
    _, xyz_camRs, _ = pcp_utils.np_vis.unproject_depth(depths,
        pix_T_cams,
        origin_T_camXs,
        camR_T_origin = None, #np.linalg.inv(self.origin_T_adam),
        clip_radius=clip_radius,
        do_vis=False)

    all_xyz_camR = np.concatenate(xyz_camRs[:], axis=0)

    print("XMIN-MAX", XMIN, XMAX)
    x_inliers = (all_xyz_camR[:, 0] > XMIN) & (all_xyz_camR[:, 0] < XMAX) #(all_xyz_camR[:, 0]) > XMIN & 
    y_inliers = (all_xyz_camR[:, 1] > YMIN) & (all_xyz_camR[:, 1] < YMAX)
    z_inliers = (all_xyz_camR[:, 2] > ZMIN) & (all_xyz_camR[:, 2] < ZMAX)

    #inliers = x_inliers & y_inliers & z_inliers
    #all_xyz_camR = all_xyz_camR[inliers, :]

    #st()
    frame = o3d.geometry.TriangleMesh.create_coordinate_frame(origin=np.zeros(3), size=frame_size)
    frame_cam = o3d.geometry.TriangleMesh.create_coordinate_frame(origin=cam_center, size=frame_size*0.5)
    object_pcd = pcp_utils.np_vis.get_pcd_object(all_xyz_camR, clip_radius=2000.0)
    things_to_print = [object_pcd, frame, frame_cam, boundary_lineset]

    pcl = o3d.geometry.PointCloud()
    pcl.points = o3d.utility.Vector3dVector(bd_pts)


    nbd_pts = bd_pts.shape[0]
    color = np.zeros((nbd_pts,3))
    color[:,0] = 1
    color[:,2] = 1
    pcl.colors = o3d.utility.Vector3dVector(color)
    things_to_print.append(pcl)
    if bbox_points_from_mesh is not None:
        bbox_lineset_from_mesh = pcp_utils.np_vis.make_lineset(bbox_points_from_mesh)
        things_to_print.append(bbox_lineset_from_mesh)
    # transform object xpos and xmat to the adam coordinate (x right, y downs)
    #bbox_lineset_from_mesh_adam = pcp_utils.np_vis.make_lineset(bbox_points_from_mesh_adam)
    o3d.visualization.draw_geometries(things_to_print) #, bbox_lineset_from_mesh_adam])


if __name__ == "__main__":
    #import sys
    #print(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("-data_name", type=str)
    parser.add_argument("-scene_id", type=int)
    args = parser.parse_args()

    print("============", args.scene_id)

    filename = '/home/htung/Desktop/BlenderTemp/%s/visual_data_Sc%s_##.npy' %(args.data_name, str(args.scene_id + 1).zfill(4))

    data = np.load(filename, allow_pickle=True).item()

    #visualize(data, clip_radius=2000)
    visualize(data, clip_radius=2, frame_size="auto")


# arr = cv2.imread(filename, cv2.IMREAD_UNCHANGED).astype(np.float32)
# arr[arr > 1000] = 0
# imageio.imwrite("depth.png", arr/np.max(arr))
# pix_T_cams = np.array([])
# origin_T_camXs = np.array([])

st()
 