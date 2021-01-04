#bvp_path = "/home/htung/Documents/2020/Fall/bvp/bvp"

#import sys
#print(sys.version_info)
#sys.path.append(bvp_path)

#import numpy as np
import bvp
#import bpy
#bpy.context.scene.render.engine = 'CYCLES'
import json
import ipdb
st=ipdb.set_trace
#from bvp.Classes.Camera import Camera
#from bvp.Classes.Scene import Scene
with open('bvp_ses1_trn1.json') as f:
  data = json.load(f)

with open('bvp_ses1_trn1_torender.json') as f:
  data2 = json.load(f)

RO = bvp.RenderOptions()
RO.resolution_x = RO.resolution_y = 256
RO.BVPopts["Type"] = "all"

for data_id in range(0, 10):
    scene_data0 = data[data_id]
    scene_data = data2[data_id]
    dbi = bvp.config
    scene_data0["background"]["dbi"] = dbi
    #import ipdb; ipdb.set_trace()
    if scene_data0["sky"] is None:
        scene_data0["sky"] = {}


    scene_data0["sky"]["dbi"] = dbi
    if "override" in scene_data0["sky"]:
        del scene_data0["sky"]["override"]
    Sky = bvp.Sky(**scene_data0["sky"])
    if scene_data0["shadow"] is None:
        scene_data0["shadow"] = {}
    scene_data0["shadow"]["dbi"] = dbi
    Cam = bvp.Camera(**scene_data0["camera"])
    Shadow = bvp.Shadow(**scene_data0["shadow"])

    Objects = []
    for obj_arg in scene_data0["objects"]:
        obj_arg["dbi"] = dbi
        Object = bvp.Object(**obj_arg)
        Objects.append(Object)

    BG = bvp.Background(**scene_data0["background"])
    nCamLoc=5

    ScnL = []
    frames = (1,1)


    #import ipdb; ipdb.set_trace()
    Scn = bvp.Scene(camera=Cam, background=BG, sky=Sky, objects=Objects, shadow=Shadow, frame_range=scene_data0["frame_range"], fname=scene_data0["render_path"], frame_rate=scene_data0["frame_rate"])
    Scn.create(RO)
    Scn.render(RO)

    out_path = scene_data0["render_path"]
    Scn.clear()


print("end")

#ScnL.append(Scn)
#SL = bvp.SceneList(ScnList=ScnL, RenderOptions=RO)
#SL.RenderSlurm(RenderGroupSize=nCamLoc)