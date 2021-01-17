import json
import cv2
import numpy as np





import pcp_utils

import ipdb
st=ipdb.set_trace

filename = '/home/htung/Desktop/BlenderTemp/Zdepth/Sc0003_##Sc0003_01_z.exr'

arr = cv2.imread(filename, cv2.IMREAD_UNCHANGED).astype(np.float32)


st()

print("hello")

#with open('/home/htung/Desktop/BlenderTemp/Zdepth/Sc0003_##Sc0003_01_z.exr') as f:
#   data = json.load(f)

# with open('bvp_ses1_trn1.json') as f:
#   data = json.load(f)


# with open('bvp_ses1_trn1_torender.json') as f:
#   data2 = json.load(f)


# st()
# print("end")
