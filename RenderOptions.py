"""
Class to control BVP Render options 
"""
# Imports
import bvp # Seems like a bad idea 
import os
import sys
import math as bnp
from .utils.blender import set_layers
from .utils.basics import fixedKeyDict
if bvp.Is_Blender:
    import bpy
    #import mathutils as bmu # "B lender M ath U tilities"
# The "type" input for compositor node creation has been arbitrarily changed 
# numerous times throughout Blender API development. This is EXTREMELY 
# IRRITATING. Nonetheless, the format may change again, so I've collected
# all the node type IDs here and use the variables below

#['R_LAYERS', 'COMPOSITE', 'R_LAYERS', 'VIEWER', 'ID_MASK', 'OUTPUT_FILE', 'R_LAYERS', 'VIEWER', 'ID_MASK', 'OUTPUT_FILE']
if sys.platform == 'darwin':
    print('Mac computer node names!')
    RLayerNodeX = 'R_LAYERS' 
    CompositorNodeX = 'COMPOSITE'
    OutputFileNodeX = 'OUTPUT_FILE'
    ViewerNodeX = 'VIEWER'
    SepRGBANodeX = 'CompositorNodeSepRGBA'
    CombRGBANodeX = 'CompositorNodeCombRGBA'
    IDmaskNodeX = 'ID_MASK'
    MathNodeX = 'CompositorNodeMath'
else:
    RLayerNodeX = 'CompositorNodeRLayers' 
    CompositorNodeX = 'CompositorNodeComposite'
    OutputFileNodeX = 'CompositorNodeOutputFile'
    ViewerNodeX = 'CompositorNodeViewer'
    SepRGBANodeX = 'CompositorNodeSepRGBA'
    CombRGBANodeX = 'CompositorNodeCombRGBA'
    IDmaskNodeX = 'CompositorNodeIDMask'
    MathNodeX = 'CompositorNodeMath'

# else:
RLayerNode = 'CompositorNodeRLayers' 
CompositorNode = 'CompositorNodeComposite'
OutputFileNode = 'CompositorNodeOutputFile'
ViewerNode = 'CompositorNodeViewer'
SepRGBANode = 'CompositorNodeSepRGBA'
CombRGBANode = 'CompositorNodeCombRGBA'
IDmaskNode = 'CompositorNodeIDMask'
MathNode = 'CompositorNodeMath'

class RenderOptions(object):
    '''Class for storing render options for a scene. 
        
    '''
    def __init__(self, blender_params=None, bvp_params=None, freestyle_settings=None):
        '''Initialize rendering options for scenes in BVP framework.

        Parameters
        ----------
        blender_params : dict
            directly updates any blender scene.render params for the scene
        bvp_params : dict
            establishes more complex BVP options (whether to initialize node setup 
            for different render passes [some work, others don't], base path for 
            render directory, and which file to use to render BVP scenes).
            fields : defaults are as follows:
                ### --- Basic file / rendering stuff --- ###
                Type : 'FirstFrame', # other options :  All,FirstAndLastFrame,'every4th'
                RenderFile : os.path.join(bvp.__path__[0],'Scripts','BlenderRender.py') # File to call to render scenes
                BasePath : '/auto/k1/mark/Desktop/BlenderTemp/', # Base render path (TO DO: replace with bvp config settings)
                
                ### --- Render passes --- ###
                Image : True # Render RGB(A) images or not (alpha layer or not determined by blender_params )
                ObjectMasks : False # Render masks for all BVP objects in scene (working)
                Zdepth : False # Render Z depth pass 
                Normals : False, # Not yet implemented
                
                ### --- Work-in-progress render passes (NOT working as of 2015.05) --- ###
                Contours : False, #Freestyle, yet to be implemented
                Motion : False, # Render motion (ground truth optical flow) pass
                Voxels : False # Create voxelized version of each scene 
                Axes : False, # based on N.Cornea code, for now 
                Clay : False, # All shape, no material / texture (over-ride w/ plain [clay] material) lighting??

        Notes
        -----
        RenderOptions does not directly modify a scene's file path; it only provides the base file (parent directory) for all rendering.
        bvpScene's "apply_opts" function should be the only function to modify with bpy.context.scene.filepath (!!) (2012.03.12)

        All the settings in here should definitely be in a separate config file. Or should just default
        more readily to the Blender defaults. (Except where we don't want them to...)

        Also, this class should sub-class the scn.render class. Maybe. Unclear what this will do
        if we want this to work outside Blender (e.g., in notebooks.)

        '''
        # Options
        self.use_freestyle = False
        self.use_antialiasing = True
        self.antialiasing_samples = '8'
        self.use_edge_enhance = False
        self.use_raytrace = True
        self.use_compositing = True
        self.use_textures = True
        self.use_sss = False
        self.use_shadows = True
        self.use_envmaps = False
        # Output resolution
        self.resolution_x = 512
        self.resolution_y = 512
        self.resolution_percentage = 100
        self.tile_x = 64 # More?
        self.tile_y = 64 # More?
        # Fields not in bpy.data.scene.render class:
        # Image settings: File format and color mode
        self.image_settings = dict(color_mode= 'RGBA',
                                   file_format = 'PNG')

        self.default_layer_opts = dict(
            layers = tuple([True]*20),
            use_zmask = False,
            use_all_z = False,
            use_solid = True, # Necessary for almost everything
            use_halo = False,
            use_ztransp = False, 
            use_sky = False,
            use_edge_enhance = False,
            use_strand = False,
            use_freestyle = False,
            use_pass_combined = False,
            use_pass_z = False,
            use_pass_vector = False,
            use_pass_normal = False,
            use_pass_uv = False,
            use_pass_mist = False,
            use_pass_object_index = False,
            use_pass_color = False,
            use_pass_diffuse = False,
            use_pass_specular = False,
            use_pass_shadow = False,
            use_pass_emit = False,
            use_pass_ambient_occlusion = False,
            use_pass_environment = False,
            use_pass_indirect = False,
            use_pass_reflection = False,
            use_pass_refraction = False,
            )
        self.freestyle_settings = dict(
            mode = 'EDITOR',
            crease_angle = 3*3.14159/4, # 135 degrees
            use_advanced_options = False, 
            use_culling = False, 
            use_material_boundaries = False,
            # use_ridge_and_valleys = False, # unclear where this is in GUI, what it does. Possibly bug.
            # use_suggestive_contours = False, # unclear where this is in GUI, what it does. Possibly bug.
            use_smoothness = False, 
            # sphere_radius = 0.1, # advanced options
            lineset_params = [dict( # in order they are in the GUI
                name = 'ImageLines',
                # Visibility 
                select_by_visibility = True,
                visibility = 'VISIBLE', # Note: need to specify extra parameters qi_start and qi_end if you want (QI) 'RANGE'
                # Edge type
                select_by_edge_types = False,
                select_silhouette = False,
                select_border = False,
                select_contour = False,
                select_suggestive_contour = False,
                select_ridge_valley = False,
                select_crease = False,
                select_edge_mark = True,
                select_external_contour = False,
                select_material_boundary = False,
                # Face marks
                select_by_face_marks = False,
                # Group
                select_by_group = False,
                # Image border
                select_by_image_border = False,
                # Possibly fill in more options here
                )],
            linestyle_params = [dict(
                name = 'ImageLines',
                color = (1.0, 0.5, 0.0),
                thickness = 1.0, 
                alpha = 1.0,
                # Too many others - look up in GUI
                )]
            )
        self.BVPopts = {
            # BVP specific rendering options
            "Image":True,
            "Voxels":False,
            "ObjectMasks":False,
            "Motion":False,
            "Zdepth":False,
            "Contours":False, #Freestyle, yet to be implemented
            "Axes":False, # based on N.Cornea code, for now - still unfinished
            "Normals":False, # Not yet implemented
            "Clay":False, # Not yet implemented - All shape, no material / texture (over-ride w/ plain [clay] material) lighting??
            "Type":'FirstFrame', # other options: "All","FirstAndLastFrame",'every4th'
            "RenderFile":os.path.join(bvp.__path__[0],'Scripts','BlenderRender.py'),
            "BasePath":'/auto/k1/mark/Desktop/BlenderTemp/', # Replace with settings!
            }
        # Disallow updates that add fields
        self.__dict__ = fixedKeyDict(self.__dict__)
        # Update defaults w/ inputs
        if not bvp_params is None:
            # TO DO: Change this variable name. Big change, tho.
            self.BVPopts.update(bvp_params)
        if not blender_params is None:
            # TO DO: Clean this shit up. Sloppy organization. 
            if 'default_layer_opts' in blender_params.keys():
                default_layer_opts = blender_params.pop('default_layer_opts')
                self.default_layer_opts.update(default_layer_opts)
            self.__dict__.update(blender_params)
        if not freestyle_settings is None:
            # This is a bad setup too. Same as above, don't want to update a 
            # dict with dicts as values (we want to keep the lower-level dicts
            # key, value pairs as well and update THEM with the inputs.)
            # This is just badly structured code.
            self.freestyle_settings.update(freestyle_settings)

    def __repr__(self):
        S = 'Class "RenderOptions":\n'+self.__dict__.__repr__()
        return S
    
    def apply_opts(self, scn=None):
        if not scn:
            # Get current scene if input not supplied
            scn = bpy.context.scene
        # Backwards compatibility:
        if not 'Voxels' in self.BVPopts:
            self.BVPopts['Voxels'] = False
        if not 'Motion' in self.BVPopts:
            self.BVPopts['Motion'] = False
        scn.use_nodes = True
        # Set only first layer to be active # WHY? This seems outdated.
        scn.layers = [True]+[False]*19
        # Get all non-function attributes
        ToSet = [x for x in self.__dict__.keys() if not hasattr(self.__dict__[x],'__call__') and not x in ['BVPopts','default_layer_opts','image_settings', 'freestyle_settings']]
        for s in ToSet:
            try:
                setattr(scn.render,s,self.__dict__[s])
            except:
                print('Unable to set attribute %s!'%s)
        # Set image settings:
        scn.render.image_settings.file_format = self.image_settings['file_format']
        scn.render.image_settings.color_mode = self.image_settings['color_mode']

        # Re-set all nodes and render layers:
        orig_layers = list(scn.render.layers)
        # Add basic image rendering layer
        imlayer = scn.render.layers.new('temp')        
        for n in scn.node_tree.nodes:
            scn.node_tree.nodes.remove(n)
        for rl in orig_layers:
            scn.render.layers.remove(rl)
        imlayer.name = 'RenderLayer'
        # Optionally add freestyle
        # NOTE: This is independent of a separate contour render layer
        if self.use_freestyle:
            imlayer.use_freestyle = True
            # Delete old linestyles / linesets? 
            for k, v in self.freestyle_settings.items():
                if not k in ('lineset_params', 'linestyle_params'):
                    setattr(imlayer.freestyle_settings, k, v)
            # Create new linesets and styles
            # Needs more error checks to assure these are the same length, or to allow them to be different lengths
            for lineset, linestyle in zip(self.freestyle_settings['lineset_params'], self.freestyle_settings['linestyle_params']):
                print(lineset)
                lset = imlayer.freestyle_settings.linesets.new(lineset['name'])
                lsty = bpy.data.linestyles.new(linestyle['name'])
                for k, v in linestyle.items():
                    setattr(lsty, k, v)
                setattr(lset, 'linestyle', lsty)
                for k, v in lineset.items():
                    setattr(lset, k, v)
        # Add basic node setup
        RL = scn.node_tree.nodes.new(type=RLayerNode)
        CompOut = scn.node_tree.nodes.new(type=CompositorNode)
        scn.node_tree.links.new(RL.outputs['Image'],CompOut.inputs['Image'])
        scn.node_tree.links.new(RL.outputs['Alpha'],CompOut.inputs['Alpha'])
        # Decide whether we're only rendering one type of output:
        single_output = sum([self.BVPopts['Image'],self.BVPopts['ObjectMasks'],self.BVPopts['Zdepth'],
                        self.BVPopts['Contours'],self.BVPopts['Axes'],self.BVPopts['Normals']])==1
        # Add compositor nodes for optional outputs:
        if self.BVPopts['Voxels']:
            self.SetUpVoxelization()
            scn.update()
            return # Special case! no other node-based options can be applied!
        if self.BVPopts['ObjectMasks']:
            self.add_object_mask_layer_nodes(single_output=single_output)
        if self.BVPopts['Motion']:
            self.add_motion_layer_nodes(single_output=single_output)
        if self.BVPopts['Zdepth']:
            self.add_zdepth_layer_nodes(single_output=single_output)
        if self.BVPopts['Contours']:
            raise Exception('Not ready yet!')
        if self.BVPopts['Axes']:
            raise Exception('Not ready yet!')
        if self.BVPopts['Normals']:
            self.add_normal_layer_nodes(single_output=single_output)
        if self.BVPopts['Clay']:
            raise Exception('Not ready yet!')
            #self.AddClayLayerNodes(Is_RenderOnlyClay=single_output)
        if not self.BVPopts['Image']:
            # Switch all properties from one of the file output nodes to the composite output
            # Grab a node
            aa = [N for N in scn.node_tree.nodes if N.type==OutputFileNodeX]
            print([a.type for a in scn.node_tree.nodes])
            fOut = aa[0]
            # Find input to this node
            Lnk = [L for L in scn.node_tree.links if L.to_node == fOut][0]
            Input = Lnk.from_socket
            # Remove all input to composite node:
            NodeComposite = [N for N in scn.node_tree.nodes if N.type==CompositorNodeX][0]
            L = [L for L in scn.node_tree.links if L.to_node==NodeComposite]
            for ll in L:
                scn.node_tree.links.remove(ll)
            # Make link from input to file output to composite output:
            scn.node_tree.links.new(Input,NodeComposite.inputs['Image'])
            # Update Scene info to reflect node info:
            scn.render.filepath = fOut.base_path+fOut.file_slots[0].path
            scn.render.image_settings.file_format = fOut.format.file_format
            # Get rid of old file output
            scn.node_tree.nodes.remove(fOut)
            # Get rid of render layer that renders image:
            RL = scn.render.layers['RenderLayer']
            scn.render.layers.remove(RL)
            # Turn off raytracing??

        scn.update()
    '''
    Notes on nodes: The following functions add various types of compositor nodes to a scene in Blender.
    These allow output of other image files that represent other "meta-information" (e.g. Z depth, 
    normals, etc) that is separate from the pixel-by-pixel color / luminance information in standard images. 
    To add nodes: NewNode = NT.nodes.new(type=NodeType) 
    See top of code for list of node types used.
    '''
    def add_object_mask_layer_nodes(self,scn=None,single_output=False):
        '''Adds compositor nodes to render out object masks.

        Parameters
        ----------
        scn : bpy.data.scene | None (default=None)
            Leave as default (None) for now. Placeholder for future code updates.
        single_output : bool
            Whether to render ONLY masks.

        Notes
        -----
        The current implementation relies on objects being linked into Blender scene (without creating proxies), or being 
        mesh objects. Older versions of the code filtered objects by whether or not they had any parent object. The old 
        way may be useful, if object insertion methods change.
        IMPORTANT: 
        If scenes are created with many objects off-camera, this code will create a mask for EVERY off-scene object. 
        These masks will not be in the scene, but blender will render an image (an all-black image) for each and 
        every one of them.
        '''
        if not scn:
            scn = bpy.context.scene
        scn.use_nodes = True
        scn.render.use_compositing = True
        ########################################################################
        ### --- First: Allocate all objects' pass indices (and groups??) --- ### 
        ########################################################################
        DisallowedNames = ['BG_','CamTar','Shadow_'] # Also constraint objects...
        Ob = [o for o in bpy.context.scene.objects if not any([x in o.name for x in DisallowedNames])]
        PassCt = 1
        for o in Ob:
            # Check for dupli groups:
            if o.type=='EMPTY':
                if o.dupli_group:
                    o.pass_index = PassCt
                    for po in o.dupli_group.objects:
                        po.pass_index = PassCt
                    set_layers(o,[0,PassCt])
                    PassCt +=1
            # Check for mesh objects:
            elif o.type=='MESH':
                o.pass_index = PassCt
                set_layers(o,[0,PassCt])
                PassCt +=1
            # Other types of objects?? 
                
        #####################################################################
        ### ---            Second: Set up render layers:              --- ### 
        #####################################################################
        RL = scn.render.layers.keys()
        if not 'ObjectMasks1' in RL:
            for iOb in range(PassCt-1):
                ObLayer =scn.render.layers.new('ObjectMasks%d'%(iOb+1))
                for k,v in self.default_layer_opts.items():
                    ObLayer.__setattr__(k,v)
                Lay = [False for x in range(20)];
                Lay[iOb+1] = True 
                ObLayer.layers = tuple(Lay)
                ObLayer.use_ztransp = True # Necessary for object indices to work for transparent materials
                ObLayer.use_pass_object_index = True # This one only
        else:
            raise Exception('ObjectMasks layers already exist!')
        ########################################################################
        ### ---            Third: Set up compositor nodes:               --- ### 
        ########################################################################
        NT = scn.node_tree
        # Object index nodes:
        PassIdx = [o.pass_index for o in scn.objects if o.pass_index < 100] # 100 is for skies!
        MaxPI = max(PassIdx)
        if bvp.Verbosity_Level > 3:
            print('I think there are %d pass indices'%(MaxPI))
        for iObIdx in range(MaxPI):
            NodeRL = NT.nodes.new(type=RLayerNode)
            NodeRL.layer = 'ObjectMasks%d'%(iObIdx+1)

            NewVwNode = NT.nodes.new(ViewerNode)
            NewIDNode = NT.nodes.new(IDmaskNode)
            NewIDOut = NT.nodes.new(OutputFileNode)
            
            VwNm = 'ID Mask %d View'%(iObIdx+1)
            NewVwNode.name = VwNm
            
            IDNm = 'ID Mask %d'%(iObIdx+1)
            NewIDNode.name = IDNm
            NewIDNode.index = iObIdx+1
            # Link nodes
            NT.links.new(NodeRL.outputs['IndexOB'],NewIDNode.inputs['ID value'])
            NT.links.new(NewIDNode.outputs['Alpha'],NewIDOut.inputs[0])
            NT.links.new(NewIDNode.outputs['Alpha'],NewVwNode.inputs['Image'])
            NewIDOut.format.file_format = 'PNG'
            NewIDOut.base_path = scn.render.filepath.replace('/Scenes/','/Masks/')
            endCut = NewIDOut.base_path.index('Masks/')+len('Masks/')
            # Set unique name per frame
            NewIDOut.file_slots[0].path = NewIDOut.base_path[endCut:]+'_m%02d'%(iObIdx+1)
            NewIDOut.name = 'Object %d'%(iObIdx)
            # Set base path
            NewIDOut.base_path = NewIDOut.base_path[:endCut]
            # Set location with NewIdNode.location = ((x,y))
            nPerRow = 8.
            Loc = bvp.bmu.Vector((bnp.modf(iObIdx/nPerRow)[0]*nPerRow,-bnp.modf(iObIdx/nPerRow)[1]))
            Offset = 250.
            Loc = Loc*Offset - bvp.bmu.Vector((nPerRow/2. * Offset - 300.,100.))  # hard-coded to be below RL node
            NewIDNode.location = Loc
            NewVwNode.location = Loc - bvp.bmu.Vector((0.,100))
            NewIDOut.location = Loc - bvp.bmu.Vector((-150.,100))

    def add_zdepth_layer_nodes(self,scn=None,single_output=False):
        '''Add Z depth node configuration to scene

        Adds compositor nodes to render out Z buffer
        '''
        if not scn:
            scn = bpy.context.scene
        scn.use_nodes = True
        scn.render.use_compositing = True
        #####################################################################
        ### ---                Set up render layers:                  --- ### 
        #####################################################################
        RL = scn.render.layers.keys()
        if not 'Zdepth' in RL:
            #bpy.ops.scene.render_layer_add() # Seems like there should be a "name" input argument, but not yet so we have to be hacky about this:
            #ObLayer = [x for x in scn.render.layers.keys() if not x in RL]
            #ObLayer = scn.render.layers[ObLayer[0]]
            ObLayer = scn.render.layers.new('Zdepth')
            for k in self.default_layer_opts.keys():
                ObLayer.__setattr__(k,self.default_layer_opts[k])
            #ObLayer.name = 'Zdepth'
            #RL.append('Zdepth')
            ObLayer.use_ztransp = True # Necessary for z depth to work for transparent materials ?
            ObLayer.use_pass_z = True # Principal interest
            ObLayer.use_pass_object_index = True # for masking out depth of sky dome 
        else:
            raise Exception('Zdepth layer already exists!')
        ########################################################################
        ### ---                Set up compositor nodes:                  --- ### 
        ########################################################################
        NT = scn.node_tree
        # Get all node names (keys)
        NodeRL = NT.nodes.new(type=RLayerNode)
        NodeRL.layer = 'Zdepth'

        # Zero out all depth info from the sky dome (the sky doesn't have any depth!)
        NodeSky = NT.nodes.new(IDmaskNode)
        NodeSky.use_antialiasing = False  #No AA for z depth! doesn't work to combine non-AA node w/ AA node!
        NodeSky.index = 100
        NT.links.new(NodeRL.outputs['IndexOB'],NodeSky.inputs['ID value'])
        NodeInv = NT.nodes.new(MathNode)
        NodeInv.operation = 'SUBTRACT'
        # Invert (ID) alpha layer, so sky values are zero, objects/bg are 1
        NodeInv.inputs[0].default_value = 1.0
        NT.links.new(NodeSky.outputs[0],NodeInv.inputs[1])
        # Mask out sky by multiplying with inverted sky mask
        NodeMult = NT.nodes.new(MathNode)
        NodeMult.operation = 'MULTIPLY'
        NT.links.new(NodeRL.outputs['Z'],NodeMult.inputs[0])
        NT.links.new(NodeInv.outputs[0],NodeMult.inputs[1])
        # Add 1000 to the sky:
        NodeMult1000 = NT.nodes.new(MathNode)
        NodeMult1000.operation = 'MULTIPLY'
        NodeMult1000.inputs[0].default_value = 1000.0
        NT.links.new(NodeMult1000.inputs[1],NodeSky.outputs[0])
        NodeAdd1000 = NT.nodes.new(MathNode)
        NodeAdd1000.operation = 'ADD'
        NodeAdd1000.inputs[0].default_value = 1000.0
        NT.links.new(NodeMult.outputs[0],NodeAdd1000.inputs[0])
        NT.links.new(NodeMult1000.outputs[0],NodeAdd1000.inputs[1])

        # Depth output node
        DepthOut = NT.nodes.new(OutputFileNode)
        DepthOut.location =  bvp.bmu.Vector((900.,300.))
        DepthOut.format.file_format = 'OPEN_EXR' # Changed 2012.10.24
        if '/Masks/' in scn.render.filepath: 
            DepthOut.base_path = scn.render.filepath[0:-4] # get rid of "_m01"
            DepthOut.base_path = DepthOut.base_path.replace('/Masks/','/Zdepth/')+'_z'
        elif '/Motion/' in scn.render.filepath:
            DepthOut.base_path = scn.render.filepath[0:-4] # get rid of "_mot"
            DepthOut.base_path = DepthOut.base_path.replace('/Motion/','/Zdepth/')+'_z'
        elif '/Normals/' in scn.render.filepath:
            DepthOut.base_path = scn.render.filepath[0:-4] # get rid of "_nor"
            DepthOut.base_path = DepthOut.base_path.replace('/Normals/','/Zdepth/')+'_z'
        else:
            DepthOut.base_path = scn.render.filepath.replace('/Scenes/','/Zdepth/')
            # Set unique name per frame
            endCut = DepthOut.base_path.index('Zdepth/')+len('Zdepth/')
            DepthOut.file_slots[0].path = DepthOut.base_path[endCut:]+'_z'
            # Set base path
            DepthOut.base_path = DepthOut.base_path[:endCut]

        NT.links.new(NodeAdd1000.outputs[0],DepthOut.inputs[0])
            
    def add_normal_layer_nodes(self,scn=None,single_output=False):
        '''Adds compositor nodes to render out surface normals.
        '''
        if not scn:
            scn = bpy.context.scene
        scn.use_nodes = True
        scn.render.use_compositing = True
        #####################################################################
        ### ---                Set up render layers:                  --- ### 
        #####################################################################
        RL = scn.render.layers.keys()
        if not 'Normals' in RL:
            bpy.ops.scene.render_layer_add() # Seems like there should be a "name" input argument, but not yet so we have to be hacky about this:
            ObLayer = [x for x in scn.render.layers.keys() if not x in RL]
            ObLayer = scn.render.layers[ObLayer[0]]
            for k in self.default_layer_opts.keys():
                ObLayer.__setattr__(k,self.default_layer_opts[k])
            ObLayer.name = 'Normals'
            RL.append('Normals')
            ObLayer.use_ztransp = True # Necessary for Normals to work for transparent materials ?
            ObLayer.use_pass_normal = True # Principal interest
            ObLayer.use_pass_object_index = True # for masking out sky dome normals
        else:
            raise Exception('Normal layer already exists!')
        ########################################################################
        ### ---                 Set up compositor nodes:                 --- ### 
        ########################################################################
        # TO DO: Make a sensible layout for these, i.e. set .location field for all nodes (not urgent...)
        NT = scn.node_tree
        NodeRL = NT.nodes.new(type=RLayerNode)
        NodeRL.layer = 'Normals'
        # Normal output nodes
        # (1) Split normal channels
        NorSpl = NT.nodes.new(type=SepRGBANode)
        NT.links.new(NodeRL.outputs['Normal'],NorSpl.inputs['Image'])
        NorSpl.location = NodeRL.location + bvp.bmu.Vector((600.,0))
        UpDown = [75.,0.,-75.]
        # (2) Zero out all normals on the sky dome (the sky doesn't really curve!)
        NodeSky = NT.nodes.new(IDmaskNode)
        NodeSky.use_antialiasing = True
        NodeSky.index = 100
        NT.links.new(NodeRL.outputs['IndexOB'],NodeSky.inputs['ID value'])
        NodeInv = NT.nodes.new(MathNode)
        NodeInv.operation = 'SUBTRACT'
        # Invert alpha layer, so sky values are zero
        NodeInv.inputs[0].default_value = 1.0
        NT.links.new(NodeSky.outputs[0],NodeInv.inputs[1])
        # (3) re-combine to RGB image
        NorCom = NT.nodes.new(type=CombRGBANode)
        NorCom.location = NodeRL.location + bvp.bmu.Vector((1050.,0.))
        # Normal values go from -1 to 1, but image formats won't support that, so we will add 1 
        # and store a floating-point value from to 0-2 in an .hdr file
        for iMap in range(3):
            # For masking out sky:
            NodeMult = NT.nodes.new(MathNode)
            NodeMult.operation = 'MULTIPLY'
            # For adding 1 to normal values:
            NodeAdd1 = NT.nodes.new(MathNode)
            NodeAdd1.operation = 'ADD'
            NodeAdd1.inputs[1].default_value = 1.0
            # Link nodes for order of computation:
            # multiply by inverse of sky alpha: 
            NT.links.new(NorSpl.outputs['RGB'[iMap]],NodeMult.inputs[0])
            NT.links.new(NodeInv.outputs['Value'],NodeMult.inputs[1])
            # Add 1:
            NT.links.new(NodeMult.outputs['Value'],NodeAdd1.inputs[0])
            # Re-combine:
            NT.links.new(NodeAdd1.outputs['Value'],NorCom.inputs['RGB'[iMap]])
        # Normal output node
        NorOut = NT.nodes.new(OutputFileNode)
        NorOut.location = NodeRL.location + bvp.bmu.Vector((1200.,0.))
        NorOut.format.file_format = 'OPEN_EXR' #'PNG'
        NorOut.name = 'fOutput Normals'
        NT.links.new(NorCom.outputs['Image'],NorOut.inputs[0])
        # If any other node is the principal node, replace (output folder) with /Normals/:
        if '/Masks/' in scn.render.filepath:
            NorOut.base_path = scn.render.filepath[0:-4] # get rid of "_m01"
            NorOut.base_path = NorOut.base_path.replace('/Masks/','/Normals/')+'_z'
        elif '/Motion/' in scn.render.filepath:
            NorOut.base_path = scn.render.filepath[0:-4] # get rid of "_mot"
            NorOut.base_path = NorOut.base_path.replace('/Motion/','/Normals/')+'_mot'
        elif '/Zdepth/' in scn.render.filepath:
            NorOut.base_path = NorOut.base_path[0:-2] # remove '_z' 
            NorOut.base_path = scn.render.filepath.replace('/Zdepth/','/Scenes/')+'_nor'
        else:
            NorOut.base_path = scn.render.filepath.replace('/Scenes/','/Normals/')
            # Set unique name per frame
            print(NorOut.base_path)
            endCut = NorOut.base_path.index('Normals/')+len('Normals/')
            NorOut.file_slots[0].path = NorOut.base_path[endCut:]+'_nor'
            # Set base path
            NorOut.base_path = NorOut.base_path[:endCut]
        NT.links.new(NorCom.outputs['Image'],NorOut.inputs[0])
    def add_motion_layer_nodes(self,scn=None,single_output=False):
        '''Adds compositor nodes to render motion (optical flow, a.k.a. vector pass)

        Parameters
        ----------
        scn : bpy scene instance | None. default = None
            Leave as default (None) for now. For potential future code upgrades
        single_output : bool
            Set True if optical flow is the only desired output of the render
        '''
        if not scn:
            scn = bpy.context.scene
        scn.use_nodes = True
        scn.render.use_compositing = True
        #####################################################################
        ### ---                Set up render layers:                  --- ### 
        #####################################################################
        RL = scn.render.layers.keys()
        if not 'Motion' in RL:
            bpy.ops.scene.render_layer_add() 
            # Seems like there should be a "name" input argument, but not yet so we have to be hacky about this:
            ObLayer = [x for x in scn.render.layers.keys() if not x in RL]
            ObLayer = scn.render.layers[ObLayer[0]]
            # /Hacky
            # Set default layer options
            for k in self.default_layer_opts.keys():
                ObLayer.__setattr__(k,self.default_layer_opts[k])
            # And set motion-specific layer options
            ObLayer.name = 'Motion'
            ObLayer.use_pass_vector = True # Motion layer
            ObLayer.use_ztransp = True # Necessary (?) for motion to work for transparent materials
            ObLayer.use_pass_z = True # Necessary (?)
            #ObLayer.use_pass_object_index = True # for masking out depth of sky dome 
            RL.append('Motion')
        else:
            raise Exception('Motion layer already exists!')
        ########################################################################
        ### ---                Set up compositor nodes:                  --- ### 
        ########################################################################
        NT = scn.node_tree
        # Get all node names (keys)
        NodeRL = NT.nodes.new(type=RLayerNode)
        NodeRL.layer = 'Motion'

        # QUESTION: Better to zero out motion in sky?? NO for now, 
        # but leave here in case we want the option later...
        if False:
            # Zero out all depth info from the sky dome (the sky doesn't have any depth!)
            NodeSky = NT.nodes.new(IDmaskNode)
            NodeSky.use_antialiasing = False  #No AA for z depth! doesn't work to combine non-AA node w/ AA node!
            NodeSky.index = 100
            NT.links.new(NodeRL.outputs['IndexOB'],NodeSky.inputs['ID value'])
            NodeInv = NT.nodes.new(MathNode)
            NodeInv.operation = 'SUBTRACT'
            # Invert (ID) alpha layer, so sky values are zero, objects/bg are 1
            NodeInv.inputs[0].default_value = 1.0
            NT.links.new(NodeSky.outputs[0],NodeInv.inputs[1])
            # Mask out sky by multiplying with inverted sky mask
            NodeMult = NT.nodes.new(MathNode)
            NodeMult.operation = 'MULTIPLY'
            NT.links.new(NodeRL.outputs['Speed'],NodeMult.inputs[0])
            NT.links.new(NodeInv.outputs[0],NodeMult.inputs[1])
            # Add 1000 to the sky:
            NodeMult1000 = NT.nodes.new(MathNode)
            NodeMult1000.operation = 'MULTIPLY'
            NodeMult1000.inputs[0].default_value = 1000.0
            NT.links.new(NodeMult1000.inputs[1],NodeSky.outputs[0])
            NodeAdd1000 = NT.nodes.new(MathNode)
            NodeAdd1000.operation = 'ADD'
            NodeAdd1000.inputs[0].default_value = 1000.0
            NT.links.new(NodeMult.outputs[0],NodeAdd1000.inputs[0])
            NT.links.new(NodeMult1000.outputs[0],NodeAdd1000.inputs[1])

        # Depth output node
        MotionOut = NT.nodes.new(OutputFileNode)
        MotionOut.location =  bvp.bmu.Vector((0.,300.))
        MotionOut.format.file_format = 'OPEN_EXR' # Changed 2012.10.24
        if '/Masks/' in scn.render.filepath: 
            MotionOut.base_path = scn.render.filepath[0:-4] # get rid of "_m01"
            MotionOut.base_path = DepthOut.base_path.replace('/Masks/','/Motion/')+'_mot'
        elif '/Normals/' in scn.render.filepath:
            MotionOut.base_path = scn.render.filepath[0:-4] # get rid of "_nor"
            MotionOut.base_path = DepthOut.base_path.replace('/Normals/','/Motion/')+'_mot'
        elif '/Zdepth/' in scn.render.filepath:
            MotionOut.base_path = scn.render.filepath[0:-2] # get rid of "_z"
            MotionOut.base_path = DepthOut.base_path.replace('/Zdepth/','/Motion/')+'_mot'
        else:
            MotionOut.base_path = scn.render.filepath.replace('/Scenes/','/Motion/')
            # Set unique name per frame
            endCut = MotionOut.base_path.index('Motion/')+len('Motion/')
            MotionOut.file_slots[0].path = MotionOut.base_path[endCut:]+'_mot'
            # Set base path
            MotionOut.base_path = MotionOut.base_path[:endCut]

        NT.links.new(NodeRL.outputs['Speed'],MotionOut.inputs[0])

    def SetUpVoxelization(self,scn=None):
        """
        Set up Blender for rendering images to create 3D voxelization of an object
        NOTE: This sets up camera, rendering engine, and materials - NOT camera trajectory!
        """
        #,xL=(-5,5),yL=(-5,5),zL=(0,10),nGrid=10,fix=None
        import math
        if scn is None:
            scn = bpy.context.scene
        # Set renderer to cycles
        scn.render.engine = 'CYCLES'
        # Set camera to cycles, fisheye equisolid, 360 deg fov
        Cam = [o for o in bpy.context.scene.objects if o.type=='CAMERA']
        if len(Cam)==1:
            Cam = Cam[0]
        else:
            raise Exception('Zero or >1 camera in your scene! WTF!!')
        Cam.data.type='PANO'
        Cam.data.cycles.fisheye_fov = math.pi*2.
        Cam.data.cycles.panorama_type='FISHEYE_EQUISOLID'

        # Get all-white cycles emission material 
        fPath,bvpfNm = os.path.split(bvp.__file__)
        fPath = os.path.join(fPath,'BlendFiles')
        fName = 'Cycles_Render.blend'
        MatNm = 'CycWhite'
        bpy.ops.wm.link_append(
            directory=os.path.join(fPath,fName)+"\\Material\\", # i.e., directory WITHIN .blend file (Scenes / Objects / Materials)
            filepath="//"+fName+"\\Material\\"+'CycWhite', # local filepath within .blend file to the material to be imported
            filename='CycWhite', # "filename" being the name of the data block, i.e. the name of the material.
            link=False,
            relative_path=False,
            )
        if bvp.Verbosity_Level >= 3:
            print('loaded "CycWhite" material!')
        
        # For all dupli-objects in scene, create proxies
        for bOb in bpy.context.scene.objects:
            # Create proxies for all objects within object
            if bOb.dupli_group:
                for o in bOb.dupli_group.objects:
                    bvp.utils.blender.grab_only(bOb)
                    bpy.ops.object.proxy_make(object=o.name) #,object=bOb.name,type=o.name)
                # Get rid of linked group now that dupli group objects are imported
                bpy.context.scene.objects.unlink(bOb)
        # Change all materials to white Cycles emission material ("CycWhite", imported above)
        for nOb in bpy.context.scene.objects:
            for m in nOb.material_slots:
                m.material = bpy.data.materials['CycWhite']

