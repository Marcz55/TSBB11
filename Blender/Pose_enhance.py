#!BPY

"""
Name: 'Pose enhancement
Blender: 277
"""
import bpy, mathutils, math, numpy

targetModelName = "teknikringen8"			#Name of model in Blender workspace
saveFilepath = "C:\\CDIO\\Tagna_bilder\\"	#The filepath to which the rendered images will be 
cameraTilt = 0;
cameraAngle = 0;
cameraX = 114;
cameraY = 45;
cameraHeight = 1;

#Assign objects

targetModel = bpy.data.objects[targetModelName]
Scene = bpy.data.scenes["Scene"]
Camera = bpy.data.objects["Camera"]

#Center camera in global coordinates
localCamera = targetModel.matrix_world.inverted()*Vector((cameraX,cameraY,0))
depthCast = targetModel.ray_cast([localCamera[0],localCamera[1],100],[0,0,-1])
depthCastGlobal = targetModel.matrix_world*depthCast[1]
bpy.context.scene.objects.active = Camera
bpy.context.active_object.location = [cameraX,cameraY,depthCastGlobal[2] + cameraHeight]
bpy.context.active_object.rotation_euler = [math.radians(90),math.radians(cameraTilt),math.radians(cameraAngle)]

def getCameraIntrinsic(write):
    Camera = bpy.data.objects["Camera"] #The camera matrix becomes "nan" if this isn't done
    CameraData = bpy.data.cameras[0]
    Scene = bpy.data.scenes["Scene"]
    #Intrinsic camera matrix
    cameraIntrinsic = Matrix().to_3x3()
    cameraIntrinsic[0][0] = -Scene.render.resolution_x/(2*tan(CameraData.angle/2))
    cameraIntrinsic[1][1] = -Scene.render.resolution_y/(2*tan(CameraData.angle/2))
    cameraIntrinsic[0][2] = Scene.render.resolution_x/2
    cameraIntrinsic[1][2] = Scene.render.resolution_y/2
    #cameraIntrinsic.transpose()
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
    direction = localXpoint-localCamera
    rayResult = object.ray_cast(localCamera,direction)
    if (rayResult[0]):
        rayLocation = object.matrix_world*rayResult[1]
    return rayLocation

def get3D(imageCoord,object):
    xPoint = imageToWorld(imageCoord)
    xPoint = Vector((xPoint[0],xPoint[1],xPoint[2]))
    localObj = object.matrix_world.inverted()*object.location
    localCamera = object.matrix_world.inverted()*Camera.location
    localXpoint = object.matrix_world.inverted()*xPoint
    direction = localXpoint-localCamera
    rayResult = object.ray_cast(localCamera,direction)
    if (rayResult[0]):
        rayLocation = object.matrix_world*rayResult[1]
    return rayLocation
