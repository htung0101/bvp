# check missing scene
import os
import ipdb
st=ipdb.set_trace
data_folder = "/home/htung/Desktop/BlenderTemp/bvp_ses1_val_output"
num_files = 59


tmp = os.listdir(data_folder)
tmp = sorted([name for name in tmp if "visual_data_" in name])
pointer = 0

for i in range(num_files):
	name = "Sc" + str(i+1).zfill(4)
	if name not in tmp[pointer]:
		print(name)
	else:
		pointer += 1

st()