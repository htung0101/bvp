blender=~/Documents/install/blender-2.91.0-linux64/blender


# render image using mark's yaml file

#blender --python data_src/render_image_from_blender.py
#blender --python render_images_grnn_data.py


$blender -P data_src/render_images_grnn_data.py -- -json_file "bvp_ses1_trn1.json"

## put output images together to make a gif video
#python data_src/make_video.py --data_dir="/home/htung/Desktop/BlenderTemp" --prefix="Sc0001_*.png"  --out_dir="/home/htung/Desktop/BlenderTemp" --outfile_prefix="test2_"


################################## visualization data #########################################
## list out objects in a blender file.
## You can also open the blender file with blender xxx.blend to see the list of objects
#$blender -P "data_src/list_file.py"  -- -filename "/home/htung/Documents/2020/Fall/mark_data/BVPdb/Background/Category_Outdoor_01.blend"


## read mark's data and make them into gif
#python data_src/visualize_data.py -fileid="0" -output_dir="vis"