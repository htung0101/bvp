"""
Class for general constraints on random distributions. 
"""
# Imports
import random
import copy
import sys # perhaps not necessary... see below
from .Object import Object # Should this be here...? Unclear. 
from .. import utils as bvpu

# TODO: Remove. Rely on numpy. 
randn = random.gauss # Takes inputs Mean, Std
rand = random.random

verbosity_level = 3

class Constraint(object):
    def __init__(self, X=None):
        """General constraints (Mean, Std, Min, Max) on random distributions (rectangular or normal)

        See sample_w_constr() for usage. Superordinate class for PosConstriant, ObConstraint, CamConstraint.

        """
        self.X = X
    def sample_w_constr(self, inpt=None):
        """Get random sample given mean, std, min, max.

        Parameters
        ----------
        inpt : list-like
            (Mean, Std, Min, Max)
        
        Notes
        -----
        If Mean (Input[0]) is None, returns uniform random sample, Min <= x <= Max
        If Mean is not None, returns x ~N(Mean, Std), Min <= x <= Max

        """
        if not inpt:
            inpt=self.X
        if not inpt:
            # Raise error??
            print('Insufficient constraints!')
            return None
        Mean, Std, Min, Max = inpt
        if not Mean is None:
            if not Std and Std!=0:
                # Raise error??
                print('Insufficient constraints!')
                return None
            n = randn(Mean, Std)
            if Max:
                n = min([n, Max])
            if Min:
                n = max([n, Min])
        else:
            if not Max:
                if not Max==0:
                    # Raise error??
                    print('Insufficient constraints!')
                    return None
            if not Min:
                Min=0
            n = rand()*(Max-Min)+Min
        return n

class PosConstraint(Constraint):
    def __init__(self, X=None, Y=None, Z=None, theta=None, phi=None, r=None, origin=(0., 0., 0.)):
        """
        Usage: PosConstraint(X=None, Y=None, Z=None, theta=None, phi=None, r=None)

        Class to store 3D position constraints for objects / cameras / whatever in Blender.

        All inputs (X, Y, ...) are 4-element tuples: (Mean, Std, Min, Max)
        For rectangular X, Y, Z constraints, only specify X, Y, and Z
        For spherical constraints, only specify theta, phi, and r 
        XYZ constraints, if present, override spherical constraints

        ML 2012.01.31
        """
        super(PosConstraint, self).__init__(X)
        # Set all inputs as class properties
        Inputs = locals()
        for i in Inputs.keys():
            if not i=='self':
                setattr(self, i, Inputs[i])
        
    #def constr2xyz(self, ConstrObj):
    def sampleXYZ(self):
        """
        Sample one position (X, Y, Z) from position distribution given spherical / XYZ constraints

        XYZ constraint will override spherical constraints if they are present.

        ML 2012.01.31
        """
        if not self.X and not self.theta:
            raise Exception('Ya hafta provide either rectangular or spherical constraints on the distribution of positions!')
        # Calling this within Blender, code should never get to here - location should be defined
        if not self.X:
            thetaOffset = 270 # To make angles in Blender more interpretable
            # Use spherical constraints  ## THETA AND PHI MAY BE BACKWARDS FROM CONVENTION!! as is its, theta is Azimuth, phi is elevation
            if not self.theta:
                theta = random.random()*360.
            else:
                theta = self.sample_w_constr(self.theta)+thetaOffset
            phi = self.sample_w_constr(self.phi)
            r = self.sample_w_constr(self.r)
            # Constrain position
            x, y, z = bvpu.bvpMath.sph2cart(r, theta, phi) # w/ theta, phi in degrees
            x = x+self.origin[0]
            y = y+self.origin[1]
            z = z+self.origin[2]
        else:
            # Use XYZ constraints:
            x = self.sample_w_constr(self.X)
            y = self.sample_w_constr(self.Y)
            z = self.sample_w_constr(self.Z)
        # Check for obstacles! 
        return x, y, z      

# Object constraints
class ObConstraint(PosConstraint):
    def __init__(self, X=None, Y=None, Z=None, 
                theta=(None, None, 0., 360.), phi=(0., 0., 0., 0.), r=(0., 5., -25., 25.), 
                origin=(0., 0., 0.), Sz=(6., 1., 3., 10.), zRot=(None, None, -180., 180.)):
        """
        Usage: ObConstraint(X=None, Y=None, Z=None, 
                theta=(None, None, 0., 360.), phi=(0., 0., 0., 0.), r=(0., 5., -25., 25.), 
                origin=(0., 0., 0.), Sz=(6., 1., 3., 10.), zRot=(None, None, -180., 180.))

        Class to store 3D position constraints for objects

        All inputs (X, Y, ...) are 4-element lists: [Mean, Std, Min, Max]
        For rectangular X, Y, Z constraints, only specify X, Y, and Z
        For spherical constraints, only specify theta, phi, and r 

        "Obst" is a list of Objects (with a size and position) that 
        are to be avoided in positioning objects

        ML 2012.10
        """
        super(ObConstraint, self).__init__(X=X, Y=Y, Z=Z, theta=theta, phi=phi, r=r, origin=origin)
        # Set all inputs as class properties
        Inputs = locals()
        for i in Inputs.keys():
            if not i=='self':
                setattr(self, i, Inputs[i])
    
    # def checkXYZS_3D(self, XYZpos, Sz, Obst=None, CheckBounds=True):
    #     """
    #     Verify that a particular position and size is acceptable given "Obst" obstacles and 
    #     the position constraints of this object (in 3-D). 
        
    #     Inputs:
    #         XYZpos = (x, y, z) position (tuple or list)
    #         Sz = scalar size
    #         Obst = list of "Object" instances to specify positions of obstacles to avoid
    #     Returns:
    #         BGboundOK = boolean; True if XYZpos is within boundary constraints
    #         ObDistOK = boolean; True if XYZpos does not overlap with other objects/obstacles 
    #     """
    #     # (1) Check distance from allowable object position boundaries (X, Y, and/or r)
    #     BGboundOK_3D = [True, True, True]
    #     if CheckBounds:
    #         X_OK, Y_OK, r_OK = True, True, True # True by default
    #         if self.X:
    #             xA = True if self.X[2] is None else (XYZpos[0]-Sz/2.)>self.X[2]
    #             xB = True if self.X[3] is None else (XYZpos[0]+Sz/2.)<self.X[3]
    #             X_OK = xA and xB
    #         if self.Y:
    #             yA = True if self.Y[2] is None else (XYZpos[1]-Sz/2.)>self.Y[2]
    #             yB = True if self.Y[3] is None else (XYZpos[1]+Sz/2.)<self.Y[3]
    #             Y_OK = yA and yB
    #         if self.r:
    #             oX, oY, oZ = self.origin
    #             R = ((XYZpos[0]-oX)**2+(XYZpos[1]-oY)**2)**.5
    #             rA = True if self.r[2] is None else (R-Sz/2.)>self.r[2]
    #             rB = True if self.r[3] is None else (R+Sz/2.)<self.r[3]
    #             r_OK = rA and rB
    #         BGboundOK_3D = [X_OK, Y_OK, r_OK] # all([...])
    #     # (2) Check distance from other objects in 3D
    #     if Obst is not None:
    #         nObj = len(Obst)
    #     else:
    #         nObj = 0
    #     TmpOb = Object(pos3D=XYZpos, size3D=Sz)
    #     ObDstOK_3D = [True]*nObj
    #     for c in range(nObj):
    #         DstThresh3D = TmpOb.size3D/2. +  Obst[c].size3D /2. 
    #         Dst3D = bvpu.bvpMath.vecDist(TmpOb.pos3D, Obst[c].pos3D)
    #         ObDstOK_3D[c] = Dst3D>DstThresh3D
    #     return BGboundOK_3D, ObDstOK_3D

    def checkXYZS_2D(self, XYZpos, Sz, Cam, Obst=None, EdgeDist=0., ObOverlap=50.):
        """
        Verify that a particular position and size is acceptable given "Obst" obstacles and 
        the position constraints of this object (in 2D images space). 
        
        Inputs:
            XYZpos = (x, y, z) position (tuple or list)
            Sz = scalar size
            Cam = Camera object (for computing perspective)
            Obst = list of "Object" instances to specify positions of obstacles to avoid
            EdgeDist = proportion of object that can go outside of the 2D image (0.-100.)
            ObOverlap = proportion of object that can overlap with other objects (0.-100.)
        Returns:
            ImBoundOK = boolean; True if 2D projection of XYZpos is less than (EdgeDist) outside of image boundary 
            ObDistOK = boolean; True if 2D projection of XYZpos overlaps less than (ObOverlap) with other objects/obstacles 
        """
        # (TODO: Make flexible for EdgeDist, ObOverlap being 0-1 or 0-100?)
        TmpOb = Object(pos3D=XYZpos, size3D=Sz)
        tmpIP_Top, tmpIP_Bot, tmpIP_L, tmpIP_R = bvpu.bvpMath.PerspectiveProj(TmpOb, Cam, ImSz=(100, 100))
        TmpObSz_X = abs(tmpIP_R[0]-tmpIP_L[0])
        TmpObSz_Y = abs(tmpIP_Bot[1]-tmpIP_Top[1])
        TmpImPos = [bvpu.bvpMath.listMean([tmpIP_R[0], tmpIP_L[0]]), bvpu.bvpMath.listMean([tmpIP_Bot[1], tmpIP_Top[1]])]
        ### --- (1) Check distance from screen edges --- ###
        Top_OK = EdgeDist < tmpIP_Top[1]
        Bot_OK = 100-EdgeDist > tmpIP_Bot[1]
        L_OK = EdgeDist < tmpIP_L[0]
        R_OK = 100-EdgeDist > tmpIP_R[0]
        EdgeOK_2D = all([Top_OK, Bot_OK, L_OK, R_OK])
        ### --- (2) Check distance from other objects in 2D --- ###
        if Obst:
            nObj = len(Obst)
        else:
            nObj = 0
        obstPos2D_List = []
        Dist_List = []
        Dthresh_List = []
        ObstSz_List = []
        ObDstOK_2D = [True for x in range(nObj)]
        for c in range(nObj):
            # Get position of obstacle
            obstIP_Top, obstIP_Bot, obstIP_L, obstIP_R = bvpu.bvpMath.PerspectiveProj(Obst[c], Cam, ImSz=(1., 1.))
            obstSz_X = abs(obstIP_R[0]-obstIP_L[0])
            obstSz_Y = abs(obstIP_Bot[1]-obstIP_Top[1])
            obstPos2D = [bvpu.bvpMath.listMean([obstIP_R[0], obstIP_L[0]]), bvpu.bvpMath.listMean([obstIP_Bot[1], obstIP_Top[1]])]
            ObstSz2D = bvpu.bvpMath.listMean([obstSz_X, obstSz_Y])
            ObjSz2D = bvpu.bvpMath.listMean([TmpObSz_X, TmpObSz_Y])
            # Note: this is an approximation! But we're ok for now (2012.10.08) with overlap being a rough measure
            PixDstThresh = (ObstSz2D/2. + ObjSz2D/2.) - (min([ObjSz2D, ObstSz2D]) * ObOverlap)
            ObDstOK_2D[c] = bvpu.bvpMath.vecDist(TmpImPos, obstPos2D) > PixDstThresh
            # For debugging
            obstPos2D_List.append(obstPos2D) 
            Dist_List.append(bvpu.bvpMath.vecDist(TmpImPos, obstPos2D))
            Dthresh_List.append(PixDstThresh)
            ObstSz_List.append(ObstSz2D)
        return EdgeOK_2D, ObDstOK_2D
    def checkSize2D(self, Obj, Cam, MinSz2D):
        """
        Usage: checkSize2D(TmpPos, Cam, MinSz2D)

        Check whether (projected) 2D size of objects meets a minimum size criterion (MinSz2D)
        
        """
        tmpIP_Top, tmpIP_Bot, tmpIP_L, tmpIP_R = bvpu.bvpMath.PerspectiveProj(Obj, Cam, ImSz=(1., 1.))
        TmpObSz_X = abs(tmpIP_R[0]-tmpIP_L[0])
        TmpObSz_Y = abs(tmpIP_Bot[1]-tmpIP_Top[1])
        SzOK_2D = sum([TmpObSz_X, TmpObSz_Y])/2. > MinSz2D
        return SzOK_2D
    def sampleXYZ(self, Sz, Cam, Obst=None, EdgeDist=0., ObOverlap=50., RaiseError=False, nIter=100, MinSz2D=0.):
        """
        Usage: sampleXYZ(self, Sz, Cam, Obst=None, EdgeDist=0., ObOverlap=50., RaiseError=False, nIter=100, MinSz2D=0.)

        Randomly sample across the 3D space of a scene, given object 
        constraints (in 3D) on that scene and the position of a camera*.
        Takes into account the size of the object to be positioned as 
        well as (optionally) the size and location of obstacles (other 
        objects) in the scene.

        * Currently only for first frame! (2012.02.19)

        Inputs: 
        Sz = object size
        Cam = Camera object
        Obst = list of Objects to be avoided 
        EdgeDist = Proportion of object by which objects must avoid the
            image border. Default=0 (touching edge is OK) Specify as a
            proportion (e.g., .1, .2, etc). Negative values mean that it
            is OK for objects to go off the side of the image. 
        ObOverlap = Proportion of image by which objects must avoid 
            the centers of other objects. Default = 50 (50% of 2D 
            object size)
        RaiseError = option to raise an error if no position can be found.
            default is False, which causes the function to return None
            instead of a position. Other errors will still be raised if 
            they occur.
        nIter = number of attempts to make at finding a scene arrangement
            that works with constraints.
        MinSz2D = minimum size of an object in 2D, given as proportion of screen (0-1)
        
        Outputs: 
        Position (x, y, z)

        NOTE: sampleXY (sampling across image space, but w/ 3D constraints)
        is currently (2012.02.22) the preferred method! (see NOTES in code)
        
        """


        """
        NOTES:
        Current method (2012.02.18) is to randomly re-sample until all 
        constraints on position are met. This can FAIL because of conflicting
        constraints (sometimes because not enough iterations were attempted, 
        sometimes because there is no solution to be found that satisfies all
        the constraints.

        sampleXY is preferred because (a) it allows for control of how often 
        objects appear at particular positions in the 2D image, and (b) it 
        seems to fail less often (it does a better job of finding a solution 
        with fewer iterations).
        
        Random re-sampling seems to be a sub-optimal way to do this; better
        would be some sort of optimized sampling method with constraints. 
        (Lagrange multipliers?) But that sounds like a pain in the ass. 
        """
        #Compute
        TooClose = True
        Iter = 1
        if Obst:
            nObj = len(Obst)
        else:
            nObj = 0
        while TooClose and Iter<nIter:
            if verbosity_level > 9:
                print("--------- Iteration %d ---------"%Iter)
            # Draw random position to start:
            c = copy.copy
            tmpC = PosConstraint(X=c(self.X), Y=c(self.Y), Z=c(self.Z), r=c(self.r), theta=c(self.theta), phi=c(self.phi))
            # change x, y position (and/or radius) limits to reflect the size of the object 
            # (can't come closer to limit than Sz/2)
            ToLimit = ['X', 'Y', 'r']
            for pNm in ToLimit:
                value = getattr(tmpC, pNm)
                if value: # (?) if any(value): (?)
                    if value[2]:
                        value[2]+=Sz/2. # increase min by Sz/2
                    if value[3]:
                        value[3]-=Sz/2. # decrease max by Sz/2
                print(pNm + '='+ str(value))
                setattr(tmpC, pNm, value)
            TmpPos = tmpC.sampleXYZ()
            BoundOK_3D, ObDstOK_3D = self.checkXYZS_3D(TmpPos, Sz, Obst=Obst)
            EdgeOK_2D, ObDstOK_2D = self.checkXYZS_2D(TmpPos, Sz, Cam, Obst=Obst, EdgeDist=EdgeDist, ObOverlap=ObOverlap)
            TmpOb = Object(pos3D=TmpPos, size3D=Sz)
            SzOK_2D = self.checkSize2D(TmpOb, Cam, MinSz2D)
            if all(ObDstOK_3D) and all(ObDstOK_2D) and all(BoundOK_3D) and EdgeOK_2D:
                TooClose = False
                TmpOb = Object(pos3D=TmpPos, size3D=Sz)
                tmpIP_Top, tmpIP_Bot, tmpIP_L, tmpIP_R = bvpu.bvpMath.PerspectiveProj(TmpOb, Cam, ImSz=(1., 1.))
                ImPos = [bvpu.bvpMath.listMean([tmpIP_R[0], tmpIP_L[0]]), bvpu.bvpMath.listMean([tmpIP_Bot[1], tmpIP_Top[1]])]
                return TmpPos, ImPos
            else:
                if verbosity_level > 9:
                    Reason = ''
                    if not all(ObDstOK_3D):
                        Add = 'Bad 3D Dist!\n'
                        for iO, O in enumerate(Obst):
                            Add += 'Dist %d = %.2f, Sz = %.2f\n'%(iO, bvpu.bvpMath.vecDist(TmpPos, O.pos3D), O.size3D)
                        Reason += Add
                    if not all(ObDstOK_2D):
                        Add = 'Bad 2D Dist!\n'
                        for iO, O in enumerate(Obst):
                            Add+= 'Dist %d: %s to %s\n'%(iO, str(obstPos2D_List[iO]), str(TmpImPos))
                        Reason+=Add
                    if not EdgeOK_2D:
                        Reason+='Edge2D bad!\n%s\n'%(str([Top_OK, Bot_OK, L_OK, R_OK]))
                    if not SzOK_2D:
                        Reason+='Object too small / size ratio bad!'
                    print('Rejected for:\n%s'%Reason)
            Iter += 1
        # Raise error if nIter is reached
        if Iter==nIter:
            if RaiseError:
                raise Exception('Iterated %d x without finding good position!'%nIter)
            else: 
                return None, None
    def sampleXY(self, Sz, Cam, Obst=None, ImPosCt=None, EdgeDist=0., ObOverlap=.50, RaiseError=False, nIter=100, MinSz2D=0.):
        """
        Usage: sampleXY(Sz, Cam, Obst=None, ImPosCt=None, EdgeDist=0., ObOverlap=.50, RaiseError=False, nIter=100, MinSz2D=0.)

        Randomly sample across the 2D space of the image, given object 
        constraints (in 3D) on the scene and the position of a camera*.
        Takes into account the size of the object to be positioned as 
        well as (optionally) the size and location of obstacles (other 
        objects) in the scene.

        * Currently only for first frame! (2012.02.19)

        Inputs: 
        Sz = object size
        Cam = Camera object
        Obst = list of Objects to be avoided 
        ImPosCt = Class that keeps track of which image positions have been sampled 
            already. Can be omitted for single scenes.
        EdgeDist = Proportion of object by which objects must avoid the
            image border. Default=0 (touching edge is OK) Specify as a
            proportion (e.g., .1, .2, etc). Negative values mean that it
            is OK for objects to go off the side of the image. 
        ObOverlap = Proportion of image by which objects must avoid 
            the centers of other objects. Default = .50 (50% of 2D 
            object size)
        RaiseError = option to raise an error if no position can be found.
            default is False, which causes the function to return None
            instead of a position. 
        nIter = number of attempts to make at finding a scene arrangement
            that works with constraints.

        Outputs: 
        Position (x, y, z), ImagePosition (x, y)

        NOTE: This is currently (2012.08) the preferred method for sampling
        object positions in a scene. See notes in sampleXYZ for more.
        
        ML 2012.02
        """

        """Check on 2D object size???"""
        #Compute
        if not ImPosCt:
            ImPosCt = bvpu.bvpMath.ImPosCount(0, 0, ImSz=1., nBins=5, e=1)
        TooClose = True
        Iter = 1
        if Obst:
            nObj = len(Obst)
        else:
            nObj = 0
        while TooClose and Iter<nIter:
            if verbosity_level > 9: 
                print("--------- Iteration %d ---------"%Iter)
            #Zbase = self.sampleXYZ(Sz, Cam)[2]
            Zbase = self.origin[2]
            # Draw random (x, y) image position to start:
            ImPos = ImPosCt.sampleXY() 
            oPosZ = bvpu.bvpMath.PerspectiveProj_Inv(ImPos, Cam, Z=100)
            oPosUp = bvpu.bvpMath.linePlaneInt(Cam.location[0], oPosZ, P0=(0, 0, Zbase+Sz/2.))
            TmpPos = oPosUp
            TmpPos[2] -= Sz/2.
            # Check on 3D bounds
            BoundOK_3D, ObDstOK_3D = self.checkXYZS_3D(TmpPos, Sz, Obst=Obst)
            # Check on 2D bounds
            EdgeOK_2D, ObDstOK_2D = self.checkXYZS_2D(TmpPos, Sz, Cam, Obst=Obst, EdgeDist=EdgeDist, ObOverlap=ObOverlap)
            # Instantiate temp object and...
            TmpOb = Object(pos3D=TmpPos, size3D=Sz)
            # ... check on 2D size
            SzOK_2D = self.checkSize2D(TmpOb, Cam, MinSz2D)
            if all(ObDstOK_3D) and all(ObDstOK_2D) and EdgeOK_2D and all(BoundOK_3D) and SzOK_2D:
                TooClose = False
                TmpPos = bvpu.basics.make_blender_safe(TmpPos, 'float')
                if verbosity_level > 7:
                    print('\nFinal image positions:')
                    for ii, dd in enumerate(obstPos2D_List):
                        print('ObPosX, Y=(%.2f, %.2f), ObstPosX, Y=%.2f, %.2f, D=%.2f'%(TmpImPos[1], TmpImPos[0], dd[1], dd[0], Dist_List[ii]))
                        print('ObSz = %.2f, ObstSz = %.2f, Dthresh = %.2f\n'%(ObjSz2D, ObstSz_List[ii], Dthresh_List[ii]))
                return TmpPos, ImPos
            else:
                if verbosity_level > 9:
                    Reason = ''
                    if not all(ObDstOK_3D):
                        Add = 'Bad 3D Dist!\n'
                        for iO, O in enumerate(Obst):
                            Add += 'Dist %d = %.2f, Sz = %.2f\n'%(iO, bvpu.bvpMath.vecDist(TmpPos, O.pos3D), O.size3D)
                        Reason += Add
                    if not all(ObDstOK_2D):
                        Add = 'Bad 2D Dist!\n'
                        for iO, O in enumerate(Obst):
                            Add+= 'Dist %d: %s to %s\n'%(iO, str(obstPos2D_List[iO]), str(TmpImPos))
                        Reason+=Add
                    if not EdgeOK_2D:
                        Reason+='Edge2D bad!\n%s\n'%(str([Top_OK, Bot_OK, L_OK, R_OK]))
                    if not EdgeOK_3D:
                        Reason+='Edge3D bad! (Object(s) out of bounds)'
                    if not SzOK_2D:
                        Reason+='Object too small / size ratio bad! '
                    print('Rejected for:\n%s'%Reason)
            Iter += 1
        # Raise error if nIter is reached
        if Iter==nIter:
            if RaiseError:
                raise Exception('MaxAttemptReached', 'Iterated %d x without finding good position!'%nIter)
            else:
                if verbosity_level > 3:
                    print('Warning! Iterated %d x without finding good position!'%nIter)
                else:
                    sys.stdout.write('.')
                return None, None
    def sampleSize(self):
        """
        sample size from self.Sz
        """
        Sz = self.sample_w_constr(self.Sz)
        return Sz
    def sampleRot(self, Cam=None):
        """
        sample rotation from self.zRot (only rotation around Z axis for now!)
        If "Cam" argument is provided, rotation is constrained to be within 90 deg. of camera!
        """
        if not Cam is None:
            import random
            VectorFn = bvpu.bvpMath.VectorFn
            # Get vector from fixation->camera
            cVec = VectorFn(Cam.fixPos[0])-VectorFn(Cam.location[0])
            # Convert to X, Y, Z Euler angles
            x, y, z = bvpu.bvpMath.vec2eulerXYZ(cVec)
            if round(random.random()):
                posNeg=1
            else:
                posNeg=-1
            zRot = z + random.random()*90.*posNeg
            zRot = bvpu.bvpMath.bnp.radians(zRot)
        else:
            zRot = self.sample_w_constr(self.zRot)
        return (0, 0, zRot)


class CamConstraint(PosConstraint):
    """
    Extension of PosConstraint to have:
    *camera speed (measured in Blender Units*) per second (assumes 15 fps)
    *pan / zoom constraints (True/False for whether pan/zoom are allowed)

    for pan, constrain radius
    for zoom, constrain theta and phi
    ... and draw another position


    NOTES: 

    What circle positions mean in Blender space, from the -y perspective @x=0 :
                  (+y)
                  90
            135         45
        180                 0  (or 360)
            225         315
                  270
                  (-y)
    THUS: to achieve 0 at dead-on (top position from -y), subtract 270 from all thetas

    """
    ## Camera position (spherical constraints)
    ## Fixation position (X, Y, Z constraints)
    def __init__(self, r=(30., 3., 20., 40.), theta=(0., 60., -135., 135.), phi=(17.5, 2.5, 12.5, 45.5), 
                origin=(0., 0., 0.), X=None, Y=None, Z=None, fixX=(0., 1., -3., 3.), 
                fixY=(0., 3., -3., 3.), fixZ=(2., .5, .0, 3.5), 
                speed=(3., 1., 0., 6.), pan=True, zoom=True):
        super(CamConstraint, self).__init__(X=X, Y=Y, Z=Z, theta=theta, phi=phi, r=r, origin=origin)
        inpt = locals()
        for i in inpt.keys():
            if not i=='self':
                setattr(self, i, inpt[i])
    def __repr__(self):
        S = 'CamConstraint:\n'+self.__dict__.__repr__()
        return(S)
    def sampleFixPos(self, frames=None, obj=None):
        """
        Sample fixation positions. Returns a list of (X, Y, Z) position tuples, nFrames long

        TO DO: 
        More constraints? max angle to change wrt camera? fixation change speed constraints?

        ML 2012.01.31
        """
        fixPos = list()
        for ii in range(len(frames)):
            # So far: No computation of how far apart the frames are, so no computation of how fast the fixation point is moving. ADD??
            if obj is None:
                TmpFixPos = (self.sample_w_constr(self.fixX), self.sample_w_constr(self.fixY), self.sample_w_constr(self.fixZ))
            else:
                ObPos = [o.pos3D for o in obj]
                ObPosX = [None, None, min([x[0] for x in ObPos]), max([x[0] for x in ObPos])] # (Mean, Std, Min, Max) for sample_w_constr
                ObPosY = [None, None, min([x[1] for x in ObPos]), max([x[1] for x in ObPos])]
                #ObPosZ = [None, None, min([x[2] for x in ObPos]), max([x[2] for x in ObPos])] # use if we ever decide to do floating objects??
                TmpFixPos = (self.sample_w_constr(ObPosX), self.sample_w_constr(ObPosY), self.sample_w_constr(self.fixZ))
            # Necessary??
            #TmpFixPos = tuple([a+b for a, b in zip(TmpFixPos, self.origin)])
            fixPos.append(TmpFixPos)
        return fixPos
    def sampleCamPos(self, frames=None):
        """
        Sample nFrames positions (X, Y, Z) from position distribution given spherical / XYZ position constraints, 
        as well as camera motion constraints (speed, pan/zoom, nFrames)

        Returns a list of (x, y, z) positions for each keyframe in "frames"

        NOTE: 
        ONLY tested up to 2 frames (i.e., len(frames)==2) as of 2012.02.15
        
        ML 2012.02
        """
        fps = 15.
        thetaOffset = 270.
        nAttempts = 1000 # Number of times to try to get whole trajectory
        nSamples = 500 # Number of positions to sample for each frame to find an acceptable next frame (within constraints)
        Failed = True
        Ct = 0
        while Failed and Ct<nAttempts:
            location = []
            Ct+=1
            for iFr, fr in enumerate(frames):
                if iFr==0: 
                    # For first frame, simply get a position
                    TmpPos = self.sampleXYZ()
                else:
                    newR, newTheta, newPhi = bvpu.bvpMath.cart2sph(TmpPos[0]-self.origin[0], TmpPos[1]-self.origin[1], TmpPos[2]-self.origin[2])
                    if verbosity_level > 5: print('computed first theta to be: %.3f'%(newTheta))
                    newTheta = bvpu.bvpMath.circ_dst(newTheta-270., 0.) # account for offset
                    if verbosity_level > 5: print('changed theta to: %.3f'%(newTheta))
                    """ All bvpu.bvpMath.cart2sph need update with origin!! """
                    if self.speed:
                        # Compute nSamples positions in a circle around last position
                        # If speed has a distribution, this will potentially allow for multiple possible positions
                        Rad = [self.sample_w_constr(self.speed) * (fr-frames[iFr-1])/fps for x in range(nSamples)]
                        # cPos will give potential new positions at allowable radii around original position
                        cPos = bvpu.bvpMath.CirclePos(Rad, nSamples, TmpPos[0], TmpPos[1]) # Gives x, y; z will be same
                        if self.X:
                            # Clip new positions if they don't satisfy original Cartesian constraints:
                            nPosXYZ = [xx+[location[iFr-1][2]] for xx in cPos if (self.X[2]<=xx[0]<=self.X[3]) and (self.Y[2]<=xx[1]<=self.Y[3])]
                            # Convert to spherical coordinates for later computations to allow zoom / pan
                            nPosSphBl = [bvpu.bvpMath.cart2sph(xx[0]-self.origin[0], xx[1]-self.origin[1], xx[2]-self.origin[2]) for xx in nPosXYZ]
                            nPosSphCs = [[xx[0], bvpu.bvpMath.circ_dst(xx[1]-thetaOffset, 0.), xx[2]] for xx in nPosSphBl]
                        elif self.theta:
                            # Convert circle coordinates to spherical coordinates (for each potential new position)
                            # "Bl" denotes un-corrected Blender coordinate angles (NOT intuitive angles, which are the units for constraints)
                            nPosSphBl = [bvpu.bvpMath.cart2sph(cPos[ii][0]-self.origin[0], cPos[ii][1]-self.origin[1], location[iFr-1][2]-self.origin[2]) for ii in range(nSamples)]
                            # returns r, theta, phi
                            # account for theta offset in original conversion from spherical to cartesian
                            # "Cs" means this is now converted to units of constraints
                            nPosSphCs = [[xx[0], bvpu.bvpMath.circ_dst(xx[1]-thetaOffset, 0.), xx[2]] for xx in nPosSphBl]
                            # Clip new positions if they don't satisfy original spherical constraints
                            nPosSphCs = [xx for xx in nPosSphCs if (self.r[2]<=xx[0]<=self.r[3]) and (self.theta[2]<=xx[1]<=self.theta[3]) and (self.phi[2]<=xx[2]<=self.phi[3])]
                            # We are now left with a list of positions in spherical coordinates that are the 
                            # correct distance away and in permissible positions wrt the original constraints
                    else: 
                        # If no speed is specified, just sample from original distribution again
                        nPosXYZ = [self.sampleXYZ() for x in range(nSamples)]
                        nPosSphBl = [bvpu.bvpMath.cart2sph(xx[0]-self.origin[0], xx[1]-self.origin[1], xx[2]-self.origin[2]) for xx in nPosXYZ]
                        nPosSphCs = [[xx[0], bvpu.bvpMath.circ_dst(xx[1]-thetaOffset, 0.), xx[2]] for xx in nPosSphBl]
                    
                    # Now filter sampled positions (nPosSphCs) by pan/zoom constraints
                    if not self.pan and not self.zoom:
                        # Repeat same position
                        pPosSphBl = [bvpu.bvpMath.cart2sph(location[iFr-1][0]-self.origin[0], location[iFr-1][1]-self.origin[1], location[iFr-1][2]-self.origin[2])]
                        pPosSphCs = [[xx[0], bvpu.bvpMath.circ_dst(xx[1]-thetaOffset, 0.), xx[2]] for xx in pPosSphBl]
                    elif self.pan and self.zoom:
                        # Any movement is possible; all positions up to now are fine
                        pPosSphCs = nPosSphCs
                    elif not self.pan and self.zoom:
                        # Constrain theta within some wiggle range
                        WiggleThresh = 3. # permissible azimuth angle variation for pure zooms, in degrees
                        thetaDist = [abs(newTheta-xx[1]) for xx in nPosSphCs]
                        pPosSphCs = [nPosSphCs[ii] for ii, xx in enumerate(thetaDist) if xx < WiggleThresh]
                    elif not self.zoom and self.pan:
                        # constrain r within some wiggle range
                        WiggleThresh = newR*.05 # permissible distance to vary in radius from center - 5% of original radius
                        rDist = [abs(newR-xx[0]) for xx in nPosSphCs]
                        pPosSphCs = [nPosSphCs[ii] for ii, xx in enumerate(rDist) if xx < WiggleThresh]             
                    else:
                        raise Exception('Something done got fucked up. This line should never be reached.')
                    if not pPosSphCs:
                        # No positions satisfy constraints!
                        break
                    else:
                        # Sample pPos (spherical coordinates for all possible new positions)    
                        TmpPosSph = pPosSphCs[random.randint(0, len(pPosSphCs)-1)]
                        r1, theta1, phi1 = TmpPosSph;
                        TmpPos = bvpu.bvpMath.sph2cart(r1, theta1+thetaOffset, phi1)
                        TmpPos = [aa+bb for (aa, bb) in zip(TmpPos, self.origin)]
                location.append(TmpPos)
                if fr==frames[-1]:
                    Failed=False
        if Failed:
            raise Exception(['Could not find camera trajectory to match constraints!'])
        else:
            return location

# THIS SHOULD BE CONVERTED TO CLASS METHOD from_background(),  
# SEPARATELY FOR EACH TYPE OF CONSTRAINT.
def GetConstr(Grp, LockZtoFloor=True): #self, bgLibDir='/auto/k6/mark/BlenderFiles/Scenes/'):
    """Get constraints on object & camera position for a particular background
    
    Parameters
    ----------


    * Camera constraints must have "cam" in their name
    * Object constraints must have "ob" in their name

    For Cartesian (XYZ) constraints: 
    * Empties must have "XYZ" in their name
    Interprets empty cubes as minima/maxima in XYZ
    Interprets empty spheres as means/stds in XYZ (not possible to have 
    non-circular Gaussians as of 2012.02)

    For polar (rho, phi, theta) constraints:
    * Empties must have "rho", "phi", or "theta" in their name, as well as _min
    Interprets empty arrows as 

    returns obConstraint, camConstraint

    TODO: 
    Camera focal length and clipping plane should be determined by "RealWorldSize" property 
    """

    """
    NOTE: 
    Starting off, this seemed like an elegant idea. In practice, it has proven to be an ugly
    pain in the ass. There must be a better way to do this.
    ML 2012.02.29
    """

    # Get camera constraints
    ConstrType = [['cam', 'fix'], ['ob']]
    thetaOffset = 270
    fn = [CamConstraint, ObConstraint]
    Out = list()
    for cFn, cTypeL in zip(fn, ConstrType):
        cParams = [dict()]
        for cType in cTypeL:
            cParams[0]['origin'] = [0, 0, 0]
            if cType=='fix':
                dimAdd = 'fix'
            else:
                dimAdd = ''
            ConstrOb = [o for o in Grp.objects if o.type=='EMPTY' and cType in o.name.lower()] 
            # Size constraints (object only!)
            SzConstr =  [n for n in ConstrOb if 'size' in n.name.lower() and cType=='ob']
            if SzConstr:
                cParams[0]['Sz'] = [None, None, None, None]
            for sz in SzConstr:
                # obsize should be done with spheres! (min/max only for now!)
                if sz.empty_draw_type=='SPHERE' and '_min' in sz.name:
                    cParams[0]['Sz'][2] = sz.scale[0]
                elif sz.empty_draw_type=='SPHERE' and '_max' in sz.name:
                    cParams[0]['Sz'][3] = sz.scale[0]   
            # Cartesian position constraints (object, camera)
            XYZconstr = [n for n in ConstrOb if 'xyz' in n.name.lower()]
            if XYZconstr:
                print('Found XYZ cartesian constraints!')
                cParams = [copy.copy(cParams[0]) for r in range(len(XYZconstr))]
                
            for iE, xyz in enumerate(XYZconstr):
                for ii, dim in enumerate(['X', 'Y', 'Z']):
                    cParams[iE][dimAdd+dim] = [None, None, None, None]
                    if xyz.empty_draw_type=='CUBE':
                        # Interpret XYZ cubes as minima / maxima
                        if dim=='Z' and cType=='ob' and LockZtoFloor:
                            # Lock to height of bottom of cube
                            cParams[iE][dimAdd+dim][2] = xyz.location[ii]-xyz.scale[ii] # min
                            cParams[iE][dimAdd+dim][3] = xyz.location[ii]-xyz.scale[ii] # max
                            cParams[iE]['origin'][ii] = xyz.location[ii]-xyz.scale[ii]
                        else:
                            cParams[iE][dimAdd+dim][2] = xyz.location[ii]-xyz.scale[ii] # min
                            cParams[iE][dimAdd+dim][3] = xyz.location[ii]+xyz.scale[ii] # max
                            cParams[iE]['origin'][ii] = xyz.location[ii]
                    elif xyz.empty_draw_type=='SPHERE':
                        # Interpret XYZ spheres as mean / std
                        cParams[iE][dimAdd+dim][0] = xyz.location[ii] # mean
                        cParams[iE][dimAdd+dim][1] = xyz.scale[0] # std # NOTE! only 1 dim for STD for now!
            # Polar position constraints (object, camera)
            if cType=='fix':
                continue
                # Fixation can only have X, Y, Z constraints for now!
            pDims = ['r', 'phi', 'theta']
            # First: find origin for spherical coordinates. Should be sphere defining radius min / max:
            OriginOb = [o for o in ConstrOb if 'r_' in o.name.lower()]
            if OriginOb:
                rptOrigin = OriginOb[0].location
                if not all([o.location==rptOrigin for o in OriginOb]):
                    raise Exception('Inconsistent origins for spherical coordinates!')
                #rptOrigin = tuple(rptOrigin)
                cParams['origin'] = tuple(rptOrigin)
            
            # Second: Get spherical constraints wrt that origin
            for dim in pDims:
                # Potentially problematic: IF xyz is already filled, fill nulls for all cParams in list of cParams
                for iE in range(len(cParams)):
                    cParams[iE][dimAdd+dim] = [None, None, None, None]
                    ob = [o for o in ConstrOb if dim in o.name.lower()]
                    for o in ob:
                        # interpret spheres or arrows w/ "_min" or "_max" in their name as limits
                        if '_min' in o.name.lower() and o.empty_draw_type=='SINGLE_ARROW':
                            cParams[iE][dimAdd+dim][2] = xyz2constr(list(o.location), dim, rptOrigin)
                            if dim=='theta':
                                cParams[iE][dimAdd+dim][2] = circ_dst(cParams[iE][dimAdd+dim][2]-thetaOffset, 0.)
                        elif '_min' in o.name.lower() and o.empty_draw_type=='SPHERE':
                            cParams[iE][dimAdd+dim][2] = o.scale[0]
                        elif '_max' in o.name.lower() and o.empty_draw_type=='SINGLE_ARROW':
                            cParams[iE][dimAdd+dim][3] = xyz2constr(list(o.location), dim, rptOrigin)
                            if dim=='theta':
                                cParams[iE][dimAdd+dim][3] = circ_dst(cParams[iE][dimAdd+dim][3]-thetaOffset, 0.)
                        elif '_max' in o.name.lower() and o.empty_draw_type=='SPHERE':
                            cParams[iE][dimAdd+dim][3] = o.scale[0]
                        elif o.empty_draw_type=='SPHERE':
                            # interpret sphere w/out "min" or "max" as mean+std
                            ## Interpretation of std here is a little fucked up: 
                            ## the visual display of the sphere will NOT correspond 
                            ## to the desired angle. But it should work.
                            cParams[iE][dimAdd+dim][0] = xyz2constr(list(o.location), dim, rptOrigin)
                            if dim=='theta':
                                cParams[iE][dimAdd+dim][0] = circ_dst(cParams[iE][dimAdd+dim][0]-thetaOffset, 0.)
                            cParams[iE][dimAdd+dim][1] = o.scale[0]
                    if not any(cParams[iE][dimAdd+dim]):
                        # If no constraints are present, simply ignore
                        cParams[iE][dimAdd+dim] = None
        toAppend = [cFn(**cp) for cp in cParams]
        if len(toAppend)==1:
            toAppend = toAppend[0]
        Out.append(toAppend)
    return Out

    
class SLConstraint(Constraint):
    """
    Class to contain constraints for properties of a scene list
    
    Necessary??
    WTF, let's see (2012.03.06)
    """
    def __init__(self):
                ### def SetScenes():
        """
        Computes concretely what will be in each scene and where. Commits probabilities into instances.
        """
        pass
        '''

        Fields to set: 

        Minutes
        Seconds
        Scenes
        ScnList
        # Compute number of scenes / duration if not given
        # Build in check for inconsistencies?
        if not self.Minutes and not self.Seconds and not self.nScenes:
            raise Exception('Please specify either nScenes, Minutes, or Seconds')
        if not self.Minutes and not self.Seconds:
            self.Seconds = self.nScenes * self.sPerScene_mean
        if not self.Minutes:
            self.Minutes = self.Seconds / 60.
        if not self.Seconds:
            self.Seconds = self.Minutes * 60.
        if not self.nScenes:
            self.nScenes = bvpu.basics.make_blender_safe(np.floor(self.Seconds / self.sPerScene_mean))

        self.nObjectsPerCat = [len(o) for o in self.Lib.objects.values()]
        # Special case for humans with poses:
        nPoses = 5
        # TEMP!
        #print('Pre-increase of human cat:')
        #print(self.nObjectsPerCat)
        Categories = self.Lib.objects.keys()
        if "Human" in Categories:
            hIdx = Categories.index("Human")
            self.nObjectsPerCat[hIdx] = self.nObjectsPerCat[hIdx] * nPoses
        self.nObjects = sum(self.nObjectsPerCat)
        # TEMP!
        #print('Post-increase of human cat:')
        #print(self.nObjectsPerCat)

        self.nBGsPerCat = [len(bg) for bg in self.Lib.bgs.values()]
        self.nBGs = sum(self.nBGsPerCat)

        self.nSkiesPerCat = [len(s) for s in self.Lib.skies.values()]
        self.nSkies = sum(self.nSkiesPerCat)

        # Frames and objects per scene will vary with the task in any given experiment... 
        # for now, this is rather simple (i.e., we will not try to account for every task we might ever want to perform)
        # Scene temporal duration
        self.nFramesPerScene = np.random.randn(self.nScenes)*self.sPerScene_std + self.sPerScene_mean
        self.nFramesPerScene = np.minimum(self.nFramesPerScene, self.sPerScene_max)
        self.nFramesPerScene = np.maximum(self.nFramesPerScene, self.sPerScene_min)
        # Note conversion of seconds to frames 
        self.nFramesPerScene = bvpu.basics.make_blender_safe(np.round(self.nFramesPerScene * self.FrameRate))
        self.nFramesTotal = sum(self.nFramesPerScene)
        # Compute nFramesTotal to match Seconds exactly 
        while self.nFramesTotal < self.Seconds*self.FrameRate:
            self.nFramesPerScene[np.random.randint(self.nScenes)] += 1
            self.nFramesTotal = sum(self.nFramesPerScene)
        while self.nFramesTotal > self.Seconds*self.FrameRate:
            self.nFramesPerScene[np.random.randint(self.nScenes)] -= 1
            self.nFramesTotal = sum(self.nFramesPerScene)
        ### --- Scene Objects --- ###
        # Set object count per scene
        self.nObjPerScene = np.round(np.random.randn(self.nScenes)*self.nObj_std + self.nObj_mean) #self.nScenes
        self.nObjPerScene = np.minimum(self.nObjPerScene, self.nObj_max)
        self.nObjPerScene = np.maximum(self.nObjPerScene, self.nObj_min)
        self.nObjPerScene = bvpu.basics.make_blender_safe(self.nObjPerScene)
        # Set object categories per scene
        self.nObjectsUsed = bvpu.basics.make_blender_safe(np.sum(self.nObjPerScene))
        
        # Get indices for objects, bgs, skies by category (imaginary part), exemplar (real part) 
        # ??? NOTE: These functions can be replaced with different functions to sample from object, background, or sky categories differently...
        if not self.obIdx:
            obIdx = self.MakeListFromLib(Type='Obj')
        else:
            obIdx = self.obIdx
        if not self.bgIdx:
            bgIdx = self.MakeListFromLib(Type='BG')
        else:
            bgIdx = self.bgIdx
        if not self.skyIdx:
            skyIdx = self.MakeListFromLib(Type='Sky')
        else:
            skyIdx = self.skyIdx
        
        ### --- Get rendering options --- ###
        self.RenderOptions = RenderOptions(self.rParams)
        ### --- Create each scene (make concrete from probablistic constraints) --- ###
        self.ScnList = []
        #print('Trying to create %d Scenes'%self.nScenes)
        for iScn in range(self.nScenes):
            # Get object category / exemplar number
            ScOb = []
            for o in range(self.nObjPerScene[iScn]):
                if verbosity_level > 3: print('Running object number %d'%o)
                # This is a shitty way to do this - better would be a matrix. Fix??
                ObTmp = obIdx.pop(0) 
                if verbosity_level > 3: print('CatIdx = %d'%ObTmp.imag)
                if verbosity_level > 3: print('ObIdx = %d'%ObTmp.real)
                Cat = self.Lib.objects.keys()[int(ObTmp.imag)]
                if verbosity_level > 3: print(Cat)
                if Cat in PosedCategories:
                    obII = int(bvpu.floor(ObTmp.real/nPoses))
                    Pose = int(bvpu.mod(ObTmp.real, nPoses))
                else:
                    obII = int(ObTmp.real)
                    Pose = None
                Grp, Fil = self.Lib.objects[Cat][obII]
                oParams = {
                    'categ':Cat, #bvpu.basics.make_blender_safe(ObTmp.imag), 
                    'exemp':Grp, #bvpu.basics.make_blender_safe(ObTmp.real), 
                    'obFile':Fil, #self.obFiles, 
                    'obLibDir':os.path.join(self.Lib.LibDir, 'Objects'), #self.obLibDir, 
                    'pose':Pose, 
                    'rot3D':None, # Set??
                    'pos3D':None, # Set??
                    }
                # Update oparams w/ self.oparams for general stuff for this scene list?? (fixed size, location, rotation???)
                # Make Rotation wrt camera???
                ScOb.append(Object(oParams))
            
            # Get BG
            if bgIdx:
                Cat = self.Lib.bgs.keys()[int(bgIdx[iScn].imag)]
                Grp, Fil = self.Lib.bgs[Cat][int(bgIdx[iScn].real)]
                bgParams = {
                    'categ':Cat, #bvpu.basics.make_blender_safe(bgIdx[iScn].imag), 
                    'exemp':Grp, #bvpu.basics.make_blender_safe(bgIdx[iScn].real), 
                    'bgFile':Fil, 
                    'bgLibDir':os.path.join(self.Lib.LibDir, 'Backgrounds'), #self.bgLibDir, 
                    #'oParams':{}
                    }
                bgParams.update(self.bgParams)
                ScBG = Background(bgParams)
            else:
                # Create default BG (empty)
                ScBG = Background(self.bgParams)
                
            # Get Sky
            if skyIdx:
                Cat = self.Lib.skies.keys()[int(skyIdx[iScn].imag)]
                Grp, Fil = self.Lib.skies[Cat][int(skyIdx[iScn].real)]          
                skyParams = {
                    'categ':Cat, #bvpu.basics.make_blender_safe(skyIdx[iScn].imag), 
                    'exemp':Grp, #bvpu.basics.make_blender_safe(skyIdx[iScn].real), 
                    'skyLibDir':os.path.join(self.Lib.LibDir, 'Skies'), #self.skyLibDir, 
                    #'skyFiles':self.skyFiles, 
                    'skyFile':Fil
                    #'skyList':self.skyList, 
                    }
                skyParams.update(self.skyParams)
                ScSky = Sky(skyParams)
            else:
                # Create default sky
                ScSky = Sky(self.skyParams)
            # Get Camera
            # GET cParams from BG??? have to do that here???
            ScCam = Camera(self.cParams)
            # Timing
            self.ScnParams = fixedKeyDict({
                'frame_start':1, 
                'frame_end':self.nFramesPerScene[iScn]
                })
            newScnParams = {
                'Num':iScn+1, 
                'Obj':ScOb, 
                'BG':ScBG, 
                'Sky':ScSky, 
                'Cam':ScCam, 
                'ScnParams':self.ScnParams, 
                }
            Scn = Scene(newScnParams)
            # Object positions are committed as scene is created...
            self.ScnList.append(Scn)
    def MakeListFromLib(self, Type='Obj'):
        """
        Usage: Idx = MakeListFromLib(Type='Obj')
        
        Creates an index/list of (objects, bgs) for each scene, given a bvpLibrary
        Input "Type" specifies which type of scene element ('Obj', 'BG', 'Sky') is to be arranged into a list. (case doesn't matter)
        
        Each (object, bg, etc) is used an equal number of times
        Potentially replace this function with other ways to sample from object categories...? 
        (sampling more from some categories than others, guaranteeing an equal number of exemplars from each category, etc)
        ML 2011.10.31
        """
        if Type.lower()=='obj':
            List = self.nObjectsPerCat
            nUsed = self.nObjectsUsed
        elif Type.lower()=='bg':
            List = self.nBGsPerCat
            nUsed = self.nScenes
        elif Type.lower()=='sky':
            List = self.nSkiesPerCat
            nUsed = self.nScenes
        else:
            raise Exception('WTF - don''t know what to do with Type=%s'%Type)
        nAvail = sum(List)
        if nAvail==0:
            return None
        Idx = np.concatenate([np.arange(o)+n*1j for n, o in enumerate(List)])
        # decide how many repetitions of each object to use
        nReps = np.floor(float(nUsed)/float(nAvail))
        nExtra = nUsed - nReps * nAvail
        ShufIdx = np.random.permutation(nAvail)[:nExtra]
        Idx = np.concatenate([np.tile(Idx, nReps), Idx[ShufIdx]])
        np.random.shuffle(Idx) # shuffle objects
        ### NOTE! this leaves open the possiblity that multiple objects of the same type will be in the same scene. OK...
        Idx = Idx.tolist()
        return Idx
        '''
