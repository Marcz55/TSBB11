#!BPY

"""
Name: 'Check point'
Blender: 277

Given two poses, pose1 and pose2, this code returns the ratio for how many of the points visible from pose 1 that are also visible from pose 2.

Given pose 1, the algorithm checks the corresponding 3D-point for a number of pixels in its image coordinates. The number of points 

Input:  The world model
        The camera location and rotation (the z-value is determined by the height over the ground)
        Intrinsic camera parameters (assuming that both cameras are identical)
        
Output: The ratio of how much of the model seen from pose 1 that is also visible in pose 2. 
"""
import bpy, mathutils, math, numpy
from mathutils import Vector
from mathutils import Matrix
from math import tan
from math import atan
from math import cos
from math import sin
from math import pi

#Start of setup---------------------------------------------------------------------------

targetModelName = "teknikringen8"			  #Name of model in Blender workspace
cameraX = 224                               #X-position of camera 1
cameraY = 60                                #Y-position of camera 1
cameraTilt = 0                              #Tilt-angle of camera 1
cameraAngle = 0                             #Angle around the z-axis of camera 1
cameraHeight = 4                        #Height over the ground of camera 1
cameraX_2 = 221.71                               #X-position of camera 2
cameraY_2 = 60                                #Y-position of camera 2
cameraTilt_2 = 0                              #Tilt-angle of camera 2
cameraAngle_2 = 0                             #Angle around the z-axis of camera 2
cameraHeight_2 = 4                        #Height over the ground of camera 2

pointCheckDensity = 10                        #The density of the point check

#Define the parameters for the camera used
cameraIntrinsicNarrative = Matrix().to_3x3()
cameraIntrinsicNarrative[0][0] = -2174.281487700746
cameraIntrinsicNarrative[1][1] = -2181.875457866787
cameraIntrinsicNarrative[0][2] = 1646.480455781699
cameraIntrinsicNarrative[1][2] = 1239.824368870457
cameraResX = 3264
cameraResY = 2448
#FOV 58.75420128917878

#End of setup--------------------------------------------------------------------------

#Assign objects
targetModel = bpy.data.objects[targetModelName]
Scene = bpy.data.scenes["Scene"]
Camera = bpy.data.objects["Camera"]

#Place camera in desired location and put at correct height over the ground
bpy.context.scene.objects.active = Camera
bpy.context.active_object.location = [cameraX,cameraY,0]
bpy.context.active_object.rotation_euler = [math.radians(90),math.radians(cameraTilt),math.radians(cameraAngle)]
localCamera = targetModel.matrix_world.inverted()*Vector((cameraX,cameraY,0))
depthCast = targetModel.ray_cast([localCamera[0],localCamera[1],100],[0,0,-1])
depthCastGlobal = targetModel.matrix_world*depthCast[1]
bpy.context.active_object.location = [cameraX,cameraY,depthCastGlobal[2] + cameraHeight]


#Adjust the object's origin so that it doesn't interfere with the raycasting
bpy.context.scene.cursor_location = Vector((0,0,0))
bpy.data.objects[targetModelName].select = True
bpy.context.scene.objects.active = targetModel
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.context.scene.objects.active = Camera


#Converts the camera matrix to use the resolution in Blender.
def convertCameraIntrinsic(intrinsic,cameraResX,cameraResY):
    Scene = bpy.data.scenes["Scene"]
    xscale = intrinsic[0][0]/min(cameraResX,cameraResY)*Scene.render.resolution_x
    yscale = intrinsic[1][1]/min(cameraResX,cameraResY)*Scene.render.resolution_y
    xcenter = Scene.render.resolution_x*intrinsic[0][2]/cameraResX
    ycenter = Scene.render.resolution_y*intrinsic[1][2]/cameraResY    
    output = Matrix().to_3x3()
    output[0][0] = xscale
    output[1][1] = yscale
    output[0][2] = xcenter
    output[1][2] = ycenter
    return output

#Sets the FOV of the camera given an intrinsic matrix
def setCameraFOV(intrinsic):
    Scene = bpy.data.scenes["Scene"]
    CameraData = bpy.data.cameras[0]
    #ratio = intrinsic[0][0]/intrinsic[1][1]
    CameraData.angle = 2*atan(-Scene.render.resolution_x/(2*intrinsic[0][0]))
    return 1

def getCameraIntrinsic():
    Camera = bpy.data.objects["Camera"]
    CameraData = bpy.data.cameras[0]
    Scene = bpy.data.scenes["Scene"]
    #Intrinsic camera matrix
    cameraIntrinsic = Matrix().to_3x3()
    cameraIntrinsic[0][0] = -Scene.render.resolution_x/(2*tan(CameraData.angle/2))
    cameraIntrinsic[1][1] = -Scene.render.resolution_y/(2*tan(CameraData.angle/2))
    cameraIntrinsic[0][2] = Scene.render.resolution_x/2
    cameraIntrinsic[1][2] = Scene.render.resolution_y/2
    return cameraIntrinsic

def getCameraExtrinsic():
    Camera = bpy.data.objects["Camera"] #Exists here in order to update the camera
    return Camera.matrix_world
            
def getP():
    shift = Matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0]])
    C = getCameraIntrinsic()
    RT = getCameraExtrinsic()
    RT_copy = RT.inverted()
    P = C*shift*RT_copy
    return P

def worldToImage(input):
    output = getP()*input
    output = output/output[2]
    return output

def imageToWorld(input):
    InvP = numpy.linalg.pinv(getP())
    InvP_copy = Matrix([[InvP[0][0],InvP[0][1],InvP[0][2]],
                         [InvP[1][0],InvP[1][1],InvP[1][2]],
                         [InvP[2][0],InvP[2][1],InvP[2][2]],
                         [InvP[3][0],InvP[3][1],InvP[3][2]]])
    output = InvP_copy*input
    output = output/output[3]
    return output
      

#Camera direction is only with respect to the Z-rotation
def getCameraDirection():
    Camera = bpy.data.objects["Camera"]
    output = Vector((cos(Camera.rotation_euler.z+pi/2), sin(Camera.rotation_euler.z+pi/2), 0))
    output.normalize()
    return output

#If the corresponding cannot be found, (0,0,0) is returned.
def get3D(imageCoord,object):
    rayLocation = Vector((0,0,0))
    posDirection = Vector((1,1,0))
    xPoint = imageToWorld(imageCoord)
    xPoint = Vector((xPoint[0],xPoint[1],xPoint[2]))
    localObj = object.matrix_world.inverted()*object.location
    localCamera = object.matrix_world.inverted()*Camera.location
    localXpoint = object.matrix_world.inverted()*xPoint
    direction = localXpoint-localCamera
    direction.normalize()
    if(getCameraDirection()*direction < 0):
        direction = -direction
    rayResult = object.ray_cast(localCamera,direction)
    if (rayResult[0]):
        rayLocation = object.matrix_world*rayResult[1]
    return rayLocation

def getPointVisible(inquiryPoint,Scene,targetModel,Camera):
    #The coordinate we want to check
    inquiryCameraPoint = worldToImage(inquiryPoint)
    #Initialize result as not having succeeded
    result = False
    #Check if the object is outside the frustum
    if(inquiryCameraPoint[0] > 0 and inquiryCameraPoint[0] < Scene.render.resolution_x and inquiryCameraPoint[1] > 0 and inquiryCameraPoint[1] < Scene.render.resolution_y):
        camToModel = get3D(inquiryCameraPoint,targetModel) - Camera.location
        camToPoint =  inquiryPoint - Camera.location
        if((camToModel-camToPoint)*getCameraDirection() > -0.01):
            result = True
    return result

#Execute---------------------------------------------------------

#Check what points on the model that are seen from the first camera pose. Points missing the model are excluded.
checkPoints = numpy.zeros((0,3))
for xpos in range(1,Scene.render.resolution_x,pointCheckDensity):
    for ypos in range(1,Scene.render.resolution_y,pointCheckDensity):
            point3D = get3D(Vector((xpos,ypos,1)),targetModel)
            if(not math.sqrt(point3D*point3D)<0.0001):
                checkPoints = numpy.append(checkPoints,[[point3D[0],point3D[1],point3D[2]]],0)

#Move the camera to the second pose
bpy.context.scene.objects.active = Camera
bpy.context.active_object.location = [cameraX_2,cameraY_2,0]
bpy.context.active_object.rotation_euler = [math.radians(90),math.radians(cameraTilt_2),math.radians(cameraAngle_2)]
localCamera = targetModel.matrix_world.inverted()*Vector((cameraX_2,cameraY_2,0))
depthCast = targetModel.ray_cast([localCamera[0],localCamera[1],100],[0,0,-1])
depthCastGlobal = targetModel.matrix_world*depthCast[1]
bpy.context.active_object.location = [cameraX_2,cameraY_2,depthCastGlobal[2] + cameraHeight_2]

#Check how many of the previously aquired 3D-points are visible from the second pose
numTrue = 0
numPoints = checkPoints.shape[0]

for it in range(0,numPoints):
    if(getPointVisible(Vector(checkPoints[it]),Scene,targetModel,Camera)):
        numTrue += 1

correspondence = numTrue/numPoints
