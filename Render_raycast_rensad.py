#!BPY

"""
Name: 'Move object and create heightmap'
Blender: 277
"""

targetModelName = "teknikringen8"			#Name of model in Blender workspace
saveFilepath = "C:\\CDIO\\Tagna_bilder\\"	#The filepath to which the rendered images will be saved
batchName = "TRtest"						#The label given to the saved inages
depthStepLength = 16						#The step length of positions where the depth will be tested
renderStepLength = 1						#The step length when iterating over the depth map
allowedDepthFactor = 0.6					#If a point on the map has a lower depth value than this factor multiplied with the model's maximum height, it will be rendered
cameraHeight = 1							#The height above the ground where the images will be rendered
numZAngles = 16								#The amount of images that will be rendered rotated around the Z-axis
numTiltAngles = 4							#The amount of images with different tilt angles between -25 and 25 degrees


#Set path
import bpy, mathutils, math, numpy

#Assign objects

targetModel = bpy.data.objects[targetModelName]
Scene = bpy.data.scenes["Scene"]
Scene.render.image_settings.file_format = 'PNG'

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
        xLoc = stepx + lowBoundX #/targetModel.dimensions[0]
        yLoc = stepy + lowBoundY#/targetModel.dimensions[1]
        rayResult = targetModel.ray_cast([xLoc,yLoc,100],[0,0,-1])
        if (rayResult[0]):
            if (rayResult[1].z > -1):
                depthMap[stepx][stepy] = rayResult[1].z
                #bpy.ops.mesh.primitive_cube_add(location=(stepx,stepy,rayResult[1].z))
            
for stepx in range (0,highBoundX-1,renderStepLength):
    for stepy in range (0,highBoundY-1,renderStepLength):
        if (depthMap[stepx][stepy] != 0 and depthMap[stepx][stepy] < allowedDepthFactor*max(max(depthMap))):
            renderMap[stepx][stepy] = 1
            #bpy.ops.mesh.primitive_cube_add(location=(stepx,stepy,1))

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

def renderPoses(xpos, ypos,zpos,numTilt, numAngle):
    Camera.location = [xpos,ypos,zpos]
    for angle in range (0,360,int(360/numAngle)):
        for tilt in range (-25,25,int(45/numTilt)):
            Camera.rotation_euler = [math.radians(90),math.radians(tilt),math.radians(angle)]
            #bpy.ops.render.render( write_still=True)
            #image = bpy.data.images['Render Result']
            #image.save_render("C:\\CDIO\\Tagna_bilder\\TRtest_x" + str(xpos) + "_y" + str(ypos) + "_a" + str(angle) + "_t" + str(tilt) + ".png", scene=Scene)
            #image.save_render(saveFilepath + batchName + "_x" + str(xpos) + "_y" + str(ypos) + "_a" + str(angle) + "_t" + str(tilt) + ".png", scene=Scene)

for stepx in range (0,highBoundX-1,renderStepLength): #0->highboundX-1
    for stepy in range (0,highBoundY-1,renderStepLength):
        if(renderMap[stepx][stepy] == 1):
            renderPoses(xpos=stepx, ypos=stepy, zpos=depthMap[stepx][stepy] + cameraHeight, numTilt=numTiltAngles, numAngle=numZAngles)
            
def getP():
    shift = Matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0]])
    C = getCameraIntrinsic(False)
    RT = getCameraExtrinsic(False)
    RT_copy = Matrix()
    RT_copy[0][0] = RT[0][0]
    RT_copy[0][1] = RT[0][1]
    RT_copy[0][2] = RT[0][2]
    RT_copy[0][3] = RT[0][3]
    RT_copy[1][0] = RT[1][0]
    RT_copy[1][1] = RT[1][1]
    RT_copy[1][2] = RT[1][2]
    RT_copy[1][3] = RT[1][3]
    RT_copy[2][0] = RT[2][0]
    RT_copy[2][1] = RT[2][1]
    RT_copy[2][2] = RT[2][2]
    RT_copy[2][3] = RT[2][3]
    RT_copy[3][0] = RT[3][0]
    RT_copy[3][1] = RT[3][1]
    RT_copy[3][2] = RT[3][2]
    RT_copy[3][3] = RT[3][3]
    RT_copy.invert()
    P = C*shift*RT_copy
    return P

def worldToImage(input):
    output = getP()*input
    output = output/output[2]
    return output

def imageToWorld(input):
    InvP = numpy.linalg.pinv(getP())
    output = InvP*input
    output = output/output[3]
    return output
      

