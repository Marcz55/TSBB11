#!BPY

"""
Name: 'Pose enhancement'
Blender: 277
"""
import bpy, mathutils, math, numpy
from mathutils import Vector
from mathutils import Matrix
from math import tan
from math import cos
from math import sin
from math import pi

targetModelName = "teknikringen8"			#Name of model in Blender workspace
dataFilepath = "C:\\CDIO\\Skript\\Maggiebild_even.npy"	#The filepath to which the rendered images will be saved
outputFilepath = "C:\\CDIO\\Skript\\3Dpunkter_even" #The filepath to where the output points will be saved
cameraHeight = 1.64;

#Define the parameters for the camera used
cameraIntrinsicNarrative = Matrix().to_3x3()
cameraIntrinsicNarrative[0][0] = 2174.281487700746
cameraIntrinsicNarrative[1][1] = 2181.875457866787
cameraIntrinsicNarrative[0][2] = 1646.480455781699
cameraIntrinsicNarrative[1][2] = 1239.824368870457
cameraResX = 3264
cameraResY = 2448

#Assign objects

targetModel = bpy.data.objects[targetModelName]
Scene = bpy.data.scenes["Scene"]
Camera = bpy.data.objects["Camera"]
Plane = bpy.data.objects["Plane"]
#Query = numpy.load(dataFilepath + "query.npy") #En testbild
#Train = numpy.load(dataFilepath + "train.npy") #En till testbild
pointList = numpy.load(dataFilepath)

cameraTilt = pointList[1][1]
cameraAngle = pointList[1][0]
cameraX = pointList[0][0]
cameraY = pointList[0][1]

#Center camera in global coordinates
localCamera = targetModel.matrix_world.inverted()*Vector((cameraX,cameraY,0))
depthCast = targetModel.ray_cast([localCamera[0],localCamera[1],100],[0,0,-1])
depthCastGlobal = targetModel.matrix_world*depthCast[1]
bpy.context.scene.objects.active = Camera
bpy.context.active_object.location = [cameraX,cameraY,depthCastGlobal[2] + cameraHeight]
bpy.context.active_object.rotation_euler = [math.radians(90),math.radians(cameraTilt),math.radians(cameraAngle)]

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

def setCameraIntrinsic(intrinsic):
    Scene = bpy.data.scenes["Scene"]
    Camera = bpy.data.objects["Camera"]
    ratio = intrinsic[0][0]/intrinsic[1][1]
    viewAngle = 2*atan(-Scene.render.resolution_x/(2*intrinsic[0][0]))
    return viewAngle

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
    if (write):
        text_file = open("IntrinsicC.txt", "w")
        text_file.write(str(cameraIntrinsic[0][0]) + " " + str(cameraIntrinsic[0][1]) + " " + str(cameraIntrinsic[0][2]) + "\n" + str(cameraIntrinsic[1][0]) + " " + str(cameraIntrinsic[1][1]) + " " + str(cameraIntrinsic[1][2]) + "\n" + str(cameraIntrinsic[2][0]) + " " + str(cameraIntrinsic[2][1]) + " " + str(cameraIntrinsic[2][2]) + "\n")
        text_file.close()
    return cameraIntrinsic

def getCameraExtrinsic(write):
    Camera = bpy.data.objects["Camera"] #Exists here in order to update the camera
    #Extrinsic camera matrix
    cameraExtrinsic = Camera.matrix_world
    if (write):
        text_file = open("ExtrinsicC.txt", "w")
        text_file.write(str(cameraIntrinsic[0][0]) + " " + str(cameraIntrinsic[0][1]) + " " + str(cameraExtrinsic[0][2]) + " " + str(cameraExtrinsic[0][3]) + "\n" + str(cameraExtrinsic[1][0]) + " " + str(cameraExtrinsic[1][1]) + " " + str(cameraExtrinsic[1][2]) + " " + str(cameraExtrinsic[1][3]) + "\n" + str(cameraExtrinsic[2][0]) + " " + str(cameraExtrinsic[2][1]) + " " + str(cameraExtrinsic[2][2]) + " " + str(cameraExtrinsic[2][3]) + "\n" + str(cameraExtrinsic[3][0]) + " " + str(cameraExtrinsic[3][1]) + " " + str(cameraExtrinsic[3][2]) + " " + str(cameraExtrinsic[3][3]) + "\n")
        text_file.close()
    return cameraExtrinsic
            
def getP():
    shift = Matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0]])
    C = getCameraIntrinsic(False)
    RT = getCameraExtrinsic(False)
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
      
def test(input,object):
    rayLocation = Vector((0,0,0))
    imageCoord = worldToImage(input)
    xPoint = imageToWorld(imageCoord)
    xPoint = Vector((xPoint[0],xPoint[1],xPoint[2]))
    localObj = object.matrix_world.inverted()*object.location
    localCamera = object.matrix_world.inverted()*Camera.location
    localXpoint = object.matrix_world.inverted()*xPoint
    direction = -(localXpoint-localCamera) #Inverterat, ty vi tittar i den första kvadranten
    rayResult = object.ray_cast(localCamera,direction)
    if (rayResult[0]):
        rayLocation = object.matrix_world*rayResult[1]
    return rayLocation

#Endast runt z-axeln
def getCameraDirection():
    Camera = bpy.data.objects["Camera"]
    output = Vector((cos(Camera.rotation_euler.z+pi/2), sin(Camera.rotation_euler.z+pi/2), 0))
    output.normalize()
    return output

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

def run(pointList,targetModel):
    output = numpy.zeros((pointList.shape[0]-2,pointList.shape[1]))
    for row in range (0,pointList.shape[0]-2):
        currentPoint = Vector((pointList[row+2][0],pointList[row+2][1],pointList[row+2][2]))
        output[row] = get3D(currentPoint,targetModel)    
    return output        

outputPoints = run(pointList,targetModel)

#for row in range(0,pointList.shape[0]):
#    bpy.ops.mesh.primitive_cube_add(location=(get3D(Vector((pointList[row][0],pointList[row][1],pointList[row][2])),targetModel)))

numpy.save(outputFilepath,outputPoints)