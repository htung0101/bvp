## NOTE! See http://western-skies.blogspot.com/2008/02/simple-complete-example-of-python.html for __getstate__() and __setstate__() methods

# Imports.
import os,types,bvp
import math as bnp
from bvp.utils.blender import AddGroup
from bvp.bvpObConstraint import bvpObConstraint
from bvp.bvpCamConstraint import bvpCamConstraint
from bvp.bvpObject import bvpObject as O
#import logger

if bvp.Is_Blender:
	import bpy
	import mathutils as bmu

# Class def
class bvpBG(object):
	'''
	Usage: bg = bvpBG(bgID=None,Lib=None) 
	
	Class to store (abstraction of) backgrounds (Floor, background objects, Object/Camera constraints, possibly lights)
	Backgrounds should be stored as scenes in one or more .blend files. File titles should be 
	"Category_BG_<BGtype>.blend", e.g. "Category_BG_Floor.blend", and all elements of the background (floor, multiple
	levels of floor, any objects) should be put into the same group (the import command used imports a group). Group 
	titles should be sensible.
	
	Inputs: 
		bgID: a unique identifier for the BG in question. Either a string 
			(interpreted to be the name of the BG group) or a lambda function
			(See bvpLibrary "getSceneComponent" function)

		Lib : is the bvpLibrary from which this BG is being drawn		

	ML 2012.03
	'''
	def __init__(self,bgID=None,Lib=None): # Add BGinfo? (w/ obstacles, camera constraints)
		# Defaults ?? Create Lib from default BG file instead ??
		self.parentFile=None
		self.grpName=None
		self.semanticCat=None
		self.objectSemanticCat='all'
		self.skySemanticCat='all'
		self.realWorldSize=100.0 # size of whole space in meters
		self.lens=50.
		self.nVertices=0
		self.nFaces=0
		# Camera position constraints w/ default values
		self.camConstraints = bvpCamConstraint()
		# Object position constraints w/ default values
		self.obConstraints = bvpObConstraint()
		# Obstacles (positions to avoid for objects)
		self.obstacles=None # list of bvpObjects
		if not bgID is None:
			if Lib is None:
				Lib = bvp.bvpLibrary()
			TmpBG = Lib.getSC(bgID,'backgrounds')
			if not TmpBG is None:
				# Replace default values with values from library
				self.__dict__.update(TmpBG)
		# lameness:
		if isinstance(self.realWorldSize,(list,tuple)):
			self.realWorldSize = self.realWorldSize[0]
	def __repr__(self):
		S = '\n ~B~ bvpBackground "%s" ~B~\n'%(self.grpName)
		if self.parentFile:
			S+='Parent File: %s\n'%self.parentFile
		if self.semanticCat:
			S+=self.semanticCat[0]
			for s in self.semanticCat[1:]: S+=', %s'%s
			S+='\n'
		# Add object semantic cat? (not done in most all scenes as of 2012.09.12)
		if self.skySemanticCat:
			S+='Skies allowed: %s'%self.skySemanticCat[0]
			for s in self.skySemanticCat[1:]: S+=', %s'%s
			S+='\n'
		S+='Size: %.2f; Camera lens: %.2f'%(self.realWorldSize,self.lens)
		if self.nVertices:
			S+='%d Verts; %d Faces'%(self.nVertices,self.nFaces)
		return(S)

	def PlaceBG(self,Scn=None):
		'''
		Adds background to Blender scene
		'''
		if not Scn:
			Scn = bpy.context.scene # Get current scene if input not supplied
		if self.grpName:
			# Add group of mesh object(s)
			fDir,fNm = os.path.split(self.parentFile)
			AddGroup(fNm,self.grpName,fDir)
		else:
			print("BG is empty!")
	def TestBG(self,frames=(1,1),ObL=(),nObj=0,EdgeDist=0.,ObOverlap=.50):
		'''
		Tests object / camera constraints to see if they are working
		** And shadows??
		'''
		Lib = bvp.bvpLibrary('/Users/mark/Documents/BlenderFiles/')
		Cam = bvp.bvpCamera(frames=frames)
		Sky = bvp.bvpSky('*'+self.skySemanticCat[0],Lib) # Choose a sky according to semantic category of BG ## RELIES ON ONLY ONE ENTRY FOR SKY SEMANTIC CAT! Should be most specific specifier...
		Scn = bvp.bvpScene(0,BG=self,Cam=Cam,Sky=Sky,FrameRange=frames)
		if not ObL and not nObj:
			ObL = [O('*animal',Lib,size3D=None),O('*vehicle',Lib,size3D=None),O('*appliance',Lib,size3D=None)]
			nObj = 0
		elif not ObL and nObj:
			ObL = [O(None,None,size3D=None) for x in range(nObj)]
		Scn.PopulateScene(ObList=ObL,ResetCam=True,RaiseError=True,nIter=100,EdgeDist=EdgeDist,ObOverlap=ObOverlap)
		if bvp.Is_Blender:
			RO = bvp.RenderOptions()
			Scn.Create(RO)
			# Add spheres if there are blank objects:
			uv = bpy.ops.mesh.primitive_uv_sphere_add
			for o in range(nObj):
				print('Sz of obj %d = %.2f'%(o,Scn.Obj[o].size3D))
				ObSz = Scn.Obj[o].size3D/2.
				pos = bmu.Vector(Scn.Obj[o].pos3D) + bmu.Vector([0,0,ObSz])
				uv(location=pos,size=ObSz)
