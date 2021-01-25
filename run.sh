#!/bin/sh
blender=~/Documents/install/blender-2.76b-linux-glibc211-x86_64/blender
# render image using mark's yaml file

#blender --python data_src/render_image_from_blender.py
#blender --python render_images_grnn_data.py

#$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn1.json -scene_id 2

scene_id=1


#$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn1.json -scene_id $scene_id

#python data_src/visualize_pointcloud.py -scene_id=1
# n=5
# #value=0
# i=0; while [ "$i" -lt 201 ]; #value in {1 2 3 4 5}
# do
#  	echo "$i"
#  	$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn1.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn1"
#     i=$((i + 1))
# done


# i=0; while [ "$i" -lt 201 ]; #value in {1 2 3 4 5}
# do
#  	echo "$i"
#  	$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn2.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn2"
#     i=$((i + 1))
# done


# i=51; while [ "$i" -lt 195 ]; #value in {1 2 3 4 5}
# do
#  	echo "$i"
#  	$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn3.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn3"
#     i=$((i + 1))
# done


# i=0; while [ "$i" -lt 201 ]; #value in {1 2 3 4 5}
# do
#  	echo "$i"
#  	$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn4.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn4"
#     i=$((i + 1))
# done


#value=$((value + 1))
#$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn1.json -scene_id $value

## put output images together to make a gif video
#python data_src/make_video.py --prefix="Sc0001_*.png"


################################## visualization data #########################################
## list out objects in a blender file.
## You can also open the blender file with blender xxx.blend to see the list of objects
#$blender -P "data_src/list_file.py" -- -filename "/home/htung/Documents/2020/Fall/mark_data/BVPdb/Background/Category_Outdoor_01.blend"


## read mark's data and make them into gif
#python data_src/visualize_data.py -fileid="0" -output_dir="vis"

## script to read json 
#python data_src/read_json.py

## 

i=0; while [ "$i" -lt 201 ]; #value in {1 2 3 4 5}
do
   echo "parsing scene $i" 
   python data_src/visualize_pointcloud.py -data_name bvp_ses1_trn1 -scene_id $i
   i=$((i + 1))
done