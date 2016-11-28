#!BPY

"""
Name: 'Render from candidate'

This script takes the camera's intrinsic and extrinsic parameters and renders the pose. If numAngles > 0, additional images will be rendered with a different z-axis rotation. For example, if numAngles = 1 with dAngle = 30, three images will be rendered (one without angular deviation, and two with +- dAngle).

Blender: 277
"""
import bpy, mathutils, math, numpy
from mathutils import Vector
from mathutils import Matrix
from math import tan
from math import atan
from math import cos
from math import sin
from math import pi

#Start of setup------------------------------------------------------------------------------------

targetModelName = "teknikringen8"			    #Name of model in Blender workspace
saveFilepath = "C:\\CDIO\\Skript\\Renderat\\"	#The filepath to which the rendered images will be saved
cameraX = 228                                   #X-position of camera  
cameraY = 60                                    #Y-position of camera
cameraTilt = 2                                  #Tilt-angle of camera 
cameraAngle = 22                                #Z-axis rotation of camera
cameraHeight = 1                                #Height of camera over the ground
dAngle = 30                                     #How much the rendered angle changes for each step in numAngles
numAngles = 1 #The number of images taken in each direction from the center (total number of images taken becomes numAngles*2 + 1)


#Define the parameters for the camera used
cameraIntrinsicNarrative = Matrix().to_3x3()
cameraIntrinsicNarrative[0][0] = -2174.281487700746
cameraIntrinsicNarrative[1][1] = -2181.875457866787
cameraIntrinsicNarrative[0][2] = 1646.480455781699
cameraIntrinsicNarrative[1][2] = 1239.824368870457
cameraResX = 3264
cameraResY = 2448
#FOV 58.75420128917878

#Assign objects

targetModel = bpy.data.objects[targetModelName]
Scene = bpy.data.scenes["Scene"]
Camera = bpy.data.objects["Camera"]

#Move camera to desired coordinate
def moveAndRender(cameraX,cameraY,cameraTilt,cameraAngle,Scene,saveFilepath,name):
    localCamera = targetModel.matrix_world.inverted()*Vector((cameraX,cameraY,0))
    depthCast = targetModel.ray_cast([localCamera[0],localCamera[1],100],[0,0,-1])
    depthCastGlobal = targetModel.matrix_world*depthCast[1]
    bpy.context.scene.objects.active = Camera
    bpy.context.active_object.location = [cameraX,cameraY,depthCastGlobal[2] + cameraHeight]
    bpy.context.active_object.rotation_euler = [math.radians(90),math.radians(cameraTilt),math.radians(cameraAngle)]
    bpy.ops.render.render( write_still=True)
    image = bpy.data.images['Render Result']
    image.save_render(saveFilepath + name + "_x" + str(cameraX) + "_y" + str(cameraY) + "_z" + str(depthCastGlobal[2]) + "_a" + str(cameraAngle) + "_t" + str(cameraTilt) + ".png", scene=Scene)
    

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

def setCameraFOV(intrinsic):
    Scene = bpy.data.scenes["Scene"]
    CameraData = bpy.data.cameras[0]
    #ratio = intrinsic[0][0]/intrinsic[1][1]
    CameraData.angle = 2*atan(-Scene.render.resolution_x/(2*intrinsic[0][0]))
    return 1

def getCameraIntrinsic(write):
    #If the variable actual is true, blender's actual camera matrix is used. Otherwise, the camera matrix given as input to this file, scaled to fit the render resolution will be returned.
    Camera = bpy.data.objects["Camera"] #The camera matrix becomes "nan" if this isn't done
    CameraData = bpy.data.cameras[0]
    Scene = bpy.data.scenes["Scene"]
    #Intrinsic camera matrix
    cameraIntrinsic = Matrix().to_3x3()
    cameraIntrinsic[0][0] = -Scene.render.resolution_x/(2*tan(CameraData.angle/2))
    cameraIntrinsic[1][1] = -Scene.render.resolution_y/(2*tan(CameraData.angle/2))
    cameraIntrinsic[0][2] = Scene.render.resolution_x/2
    cameraIntrinsic[1][2] = Scene.render.resolution_y/2
    return cameraIntrinsic
     

#MAIN----------------------------------------------------------------

#Convert given camera matrix to our resolution
convertedIntrinsic = convertCameraIntrinsic(cameraIntrinsicNarrative,cameraResX,cameraResY)
setCameraFOV(convertedIntrinsic)

moveAndRender(cameraX,cameraY,cameraTilt,cameraAngle,Scene,saveFilepath,"Output")

if (numAngles > 0):
    for it in range(1,numAngles+1):
        moveAndRender(cameraX,cameraY,cameraTilt,cameraAngle + it*dAngle,Scene,saveFilepath,"Output")
        moveAndRender(cameraX,cameraY,cameraTilt,cameraAngle - it*dAngle,Scene,saveFilepath,"Output")
    


#hej = numpy.zeros((outputPoints.shape[0],outputPoints.shape[1]))
#hejklar = numpy.zeros((outputPoints.shape[0],outputPoints.shape[1]))
#for row in range(0,outputPoints.shape[0]):
#    hej[row] = worldToImage(Vector((outputPoints[row][0],outputPoints[row][1],outputPoints[row][2],1)))
#    hejklar[row] = hej[row] - Vector((pointList[row+2][0],Scene.render.resolution_y-pointList[row+2][1],pointList[row+2][2]))
    
#for row in range(0,pointList.shape[0]):
#    bpy.ops.mesh.primitive_cube_add(location=(get3D(Vector((pointList[row][0],512-pointList[row][1],pointList[row][2])),targetModel)))