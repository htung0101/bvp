import bpy
import os
import argparse
import ipdb
st = ipdb.set_trace

import sys
sys.path.append(os.environ['BVP_SOURCE_DIR'])
import bvp_utils

def debug_print(msg):
    print(msg)

def list_referenced_images():
    rval = set()
    for img in bpy.data.images:
        if img.filepath is not None:
            debug_print ("IMAGE %s"%img.filepath)
            rval.add(bpy.path.abspath(img.filepath))
    return rval

def paths_for_vse_strip(strip):
    if hasattr(strip, "filepath"):
        return [ strip.filepath ]
    if hasattr(strip, "directory"):
        return [ strip.directory+elt.filename for elt in strip.elements ]
    return []

def list_vse_references():
    rval = set()
    for scn in bpy.data.scenes:
        if scn.sequence_editor is not None:
            for strip in scn.sequence_editor.sequences_all:
                for path in paths_for_vse_strip(strip):
                    debug_print("VSE %s"%path)
                    rval.add(bpy.path.abspath(path))
    return rval


def file_is_used(f, used):
    if f in used:
        return True

    # OMG, windows.  WTF?
    for f2 in used:
        if os.path.samefile(f2, f):
            return True

    return False


def mission1():
    used  = set()
    used.update( list_referenced_images() )
    used.update( list_vse_references() )

    dir = "/home/htung/Documents/2020/Fall/mark_data/BVPdb/Background"
    for f in sorted(os.listdir(dir)):
        f2 = os.path.join(dir, f)
        if file_is_used(f2, used):
            print("USED\t%s"%f2)
        else:
            print("UNUSED\t%s"%f2)


#mission1()
if __name__ == "__main__":
    #import sys
    #print(sys.argv)
    parser = bvp_utils.utils.ArgumentParserForBlender()
    parser.add_argument("-filename", type=str, default="")
    #parser.add_argument("-P", type=str, default="")
    args = parser.parse_args()

    fp = args.filename
    print("filename", fp)
    #fp = "/home/htung/Documents/2020/Fall/mark_data/BVPdb/Background/Category_Outdoor_01.blend"
    with bpy.data.libraries.load(fp) as (data_in, data_out):
       pass
    print(data_in.collections)

#['Group.004', 'Group.003', 'Group.002', 'Group.001', 'Group']