#!BPY

"""
Name: 'Move object and create heightmap'
Blender: 277
"""
targetModelName = "teknikringen8"
#outputPoses = open('Poses.txt')

#Set path
import bpy, mathutils, math

#Assign objects
Camera = bpy.data.objects["Camera"]
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

depthStepLength = 16
renderStepLength = 1
allowedDepthFactor = 0.6
rayXMax = int(targetModel.dimensions[1])
rayYMax = int(targetModel.dimensions[0])
lowBoundX = int(cornerX)
lowBoundY = int(cornerY)
highBoundX = rayXMax-int(cornerX)
highBoundY = rayYMax-int(cornerY)
cameraHeight = 1

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
            
def renderPoses(xpos, ypos,zpos,numTilt, numAngle):
    Camera.location = [xpos,ypos,zpos]
    for angle in range (0,360,int(360/numAngle)):
        for tilt in range (-45,45,int(90/numTilt)):
            Camera.rotation_euler = [math.radians(90),math.radians(tilt),math.radians(angle)]
            #bpy.ops.render.render( write_still=True)
            #image = bpy.data.images['Render Result']
            #image.save_render("C:\\CDIO\\Tagna_bilder\\TRtest_x" + str(xpos) + "_y" + str(ypos) + "_a" + str(angle) + "_t" + str(tilt) + ".png", scene=Scene)
            
for stepx in range (0,highBoundX-1,renderStepLength): #0->highboundX-1
    for stepy in range (0,highBoundY-1,renderStepLength):
        if(renderMap[stepx][stepy] == 1):
            renderPoses(xpos=stepx, ypos=stepy, zpos=depthMap[stepx][stepy] + cameraHeight, numTilt=4, numAngle=10)
            


          

#Render a number of images
#for step in range(0,no_steps):
#     bpy.data.scenes["Scene"].render.filepath = 'C:\CDIO\Tagna_bilder\testbild%d.png' %step
#     bpy.ops.render.render( write_still=True)
#     image = bpy.data.images['Render Result']
#     image.save_render("C:\\CDIO\\Tagna_bilder\\testbild" + str(step) +".png", scene=Scene)
