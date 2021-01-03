#bvp_path = "/home/htung/Documents/2020/Fall/bvp/bvp"

#import sys
#print(sys.version_info)
#sys.path.append(bvp_path)



from Classes.Camera import Camera
import bvp


Cam = Camera()
nCamLoc=5
RO = bvp.RenderOptions()
RO.resolution_x = RO.resolution_y = 256
ScnL = []

S = Scene(Num=None, BG=None, Sky=None, Obj=None, 
          Shadow=None, Cam=Cam, FrameRange=frames, 
          fpath=fpath, 
          FrameRate=15)
ScnL.append(S)
SL = SceneList(ScnList=ScnL, RenderOptions=RO)
SL.RenderSlurm(RenderGroupSize=nCamLoc)