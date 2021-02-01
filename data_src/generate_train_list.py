import os
import random

# make training list

path =  "/home/htung/Desktop/BlenderTemp"
#folders = ["bvp_ses1_trn1", "bvp_ses1_trn2", "bvp_ses1_trn3", "bvp_ses1_trn4"]
#output_file = "mark_data_train.txt"
folders = ["bvp_ses1_trn4_output"]
output_file = "mark_testdata_trn4.txt"
shuffle = False

files = []
for folder in folders:

    for file in os.listdir(os.path.join(path, folder)):
    	if file.endswith(".npy"):
            files.append(os.path.join(folder, file))

if shuffle:
    random.shuffle(files)
else:
	files = sorted(files)
with open(output_file, "w") as f:
    for file in files:
        f.writelines(file + "\n")
