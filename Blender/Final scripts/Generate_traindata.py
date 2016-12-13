#!BPY

"""
Name: 'Move object and create heightmap'
Blender: 277

This script is intended for the generation of training data. As for the model, the "ground" is assumed to have a normal in the z-direction, and to be approximately flat (when it comes to the height of the ground itself). The ground plane is assumed to lie approximately in the xy-plane.
"""

import bpy, mathutils, math, numpy
from random import randint

#Start of setup-------------------------------------------------------------------------------------

targetModelName = "teknikringen8"			#Name of model in Blender workspace
saveFilepath = "C:\\CDIO\\Tagna_bilder\\"	#The filepath to which the rendered images will be saved
batchName = "TRtest"						#The label given to the saved images
depthStepLength = 50						#The step length of positions where the depth will be tested
renderStepLength = 1						#The step length when iterating over the depth map
allowedDepthFactor = 0.6					#If a point on the map has a lower depth value than this factor multiplied with the model's maximum height, it will be rendered
cameraHeight = 1							#The height above the ground where the images will be rendered
numZAngles = 2								#The amount of images that will be rendered rotated around the Z-axis
numTiltAngles = 2							#The number of times the same position and Z-angle will be rendered. For use with random noise.

#Random parameters - used for creating noise in training data. These random parameters will be generated for each new image.

varPosition = 2                             #Shift the position randomly in the xy-plane. Max movement is +-varPosition.  
maxTilt = 15                                #Introduce a random tilt with limits +-maxTilt degrees.
varZAngle = 10                              #Introduce a random deviation in rotation around the Z-axis with limits +- varZangle degrees.
varPitch = 20                               #Introduce a random noise for the angle around the X-axis, ranging from 0 to varPitch degrees.

#End of setup---------------------------------------------------------------------------------------

#Assign objects
targetModel = bpy.data.objects[targetModelName]
Scene = bpy.data.scenes["Scene"]
Scene.render.image_settings.file_format = 'PNG'
Camera = bpy.data.objects["Camera"]

#Center camera in global coordinates
bpy.context.scene.objects.active = Camera
bpy.context.active_object.location = [0,0,0]
bpy.context.active_object.rotation_euler = [0,0,0]
#Center object in global coordinates
bpy.context.scene.objects.active = targetModel
bpy.context.active_object.location = [0,0,0]

#Get x- and y-coords for the lower corner in the fourth quadrant
cornerX = targetModel.bound_box[0][0]
cornerY = targetModel.bound_box[0][1]

#Place the model in the first quadrant of the x,y-plane
targetModel.location = mathutils.Vector((-cornerX,-cornerY,0))

#Render properties
rayXMax = int(targetModel.dimensions[1])
rayYMax = int(targetModel.dimensions[0])
lowBoundX = int(cornerX)
lowBoundY = int(cornerY)
highBoundX = rayXMax-int(cornerX)
highBoundY = rayYMax-int(cornerY)


#Create empty list for the height map of the model
depthMap = [[0 for y in range (highBoundY)]for x in range (highBoundX)]
renderMap = [[0 for y in range (highBoundY)]for x in range (highBoundX)]

#Code for looping through the object, creating a heightmap
for stepx in range (0,highBoundX-1,depthStepLength):
    for stepy in range (0,highBoundY-1,depthStepLength):
        #Plocka ut det högsta z-värdet på denna koordinat
        xLoc = stepx + lowBoundX
        yLoc = stepy + lowBoundY
        rayResult = targetModel.ray_cast([xLoc,yLoc,100],[0,0,-1])
        if (rayResult[0]):
            if (rayResult[1].z > -1):
                depthMap[stepx][stepy] = rayResult[1].z
            
for stepx in range (0,highBoundX-1,renderStepLength):
    for stepy in range (0,highBoundY-1,renderStepLength):
        if (depthMap[stepx][stepy] != 0 and depthMap[stepx][stepy] < allowedDepthFactor*max(max(depthMap))):
            renderMap[stepx][stepy] = 1

def getCameraIntrinsic(write):
    Camera = bpy.data.objects["Camera"]
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
    Camera = bpy.data.objects["Camera"]
    #Extrinsic camera matrix
    cameraExtrinsic = Camera.matrix_world
    if (write):
        text_file = open("ExtrinsicC.txt", "w")
        text_file.write(str(cameraIntrinsic[0][0]) + " " + str(cameraIntrinsic[0][1]) + " " + str(cameraExtrinsic[0][2]) + " " + str(cameraExtrinsic[0][3]) + "\n" + str(cameraExtrinsic[1][0]) + " " + str(cameraExtrinsic[1][1]) + " " + str(cameraExtrinsic[1][2]) + " " + str(cameraExtrinsic[1][3]) + "\n" + str(cameraExtrinsic[2][0]) + " " + str(cameraExtrinsic[2][1]) + " " + str(cameraExtrinsic[2][2]) + " " + str(cameraExtrinsic[2][3]) + "\n" + str(cameraExtrinsic[3][0]) + " " + str(cameraExtrinsic[3][1]) + " " + str(cameraExtrinsic[3][2]) + " " + str(cameraExtrinsic[3][3]) + "\n")
        text_file.close()
    return cameraExtrinsic

def renderPoses(xpos, ypos,zpos,numTilt, numAngle,varPos,varTilt,varAngle,varLookX):
    xposc = xpos
    yposc = ypos
    Camera.location = [xpos,ypos,zpos]
    for anglec in range (0,360,int(360/numAngle)):
        for tiltc in range (-25,25,int(45/numTilt)):
            xpos = xposc+randint(-varPos,varPos)
            ypos = yposc+randint(-varPos,varPos)
            tilt = randint(-varTilt,varTilt)
            angle = anglec + randint(-varAngle,varAngle)
            Camera.rotation_euler = [math.radians(90 + randint(-0,varLookX)),math.radians(tilt),math.radians(angle)]
            bpy.ops.render.render( write_still=True)
            image = bpy.data.images['Render Result']
            image.save_render(saveFilepath + batchName + "_x" + str(xpos) + "_y" + str(ypos) + "_a" + str(angle) + "_t" + str(tilt) + ".png", scene=Scene)

for stepx in range (0,highBoundX-1,renderStepLength): 
    for stepy in range (0,highBoundY-1,renderStepLength):
        if(renderMap[stepx][stepy] == 1):
            renderPoses(xpos=stepx, ypos=stepy, zpos=depthMap[stepx][stepy] + cameraHeight, numTilt=numTiltAngles, numAngle=numZAngles, varPos = varPosition, varTilt = maxTilt, varAngle = varZAngle, varLookX = varPitch)
