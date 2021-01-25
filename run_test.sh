#!/bin/sh
blender=~/Documents/install/blender-2.76b-linux-glibc211-x86_64/blender

# this script tries to pack rendered rgb and depth into grnn format
# this is mainly for testing

#i=2
#$blender -b -P data_src/grnn_data_for_test.py -- -json_file bvp_ses1_trn1.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn1_output"

#i=0
#$blender -b -P data_src/grnn_data_for_test.py -- -json_file bvp_ses1_trn1.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn1_output2"

i=0; while [ "$i" -lt 201 ]; #value in {1 2 3 4 5}
do
 	echo "$i"
 	$blender -b -P data_src/grnn_data_for_test.py -- -json_file bvp_ses1_trn1.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn1_output"
    i=$((i + 1))
done

i=0; while [ "$i" -lt 201 ]; #value in {1 2 3 4 5}
do
 	echo "$i"
 	$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn2.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn2_output"
    i=$((i + 1))
done


i=0; while [ "$i" -lt 195 ]; #value in {1 2 3 4 5}
do
 	echo "$i"
 	$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn3.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn3_output"
    i=$((i + 1))
done


i=0; while [ "$i" -lt 201 ]; #value in {1 2 3 4 5}
do
 	echo "$i"
 	$blender -b -P data_src/render_images_grnn_data.py -- -json_file bvp_ses1_trn4.json -scene_id $i -output_dir "/home/htung/Desktop/BlenderTemp/bvp_ses1_trn4_output"
    i=$((i + 1))
done
#python data_src/visualize_pointcloud.py -data_name bvp_ses1_trn1_output -scene_id $i