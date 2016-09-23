#!BPY

"""
Name: 'Test to move camera'
Blender: 277
"""
targetModelName = "Cube"

#Set path
no_steps = 2;

import bpy, mathutils

#Assign objects
Camera = bpy.data.objects["Camera"]
targetModel = bpy.data.objects[targetModelName]
Scene = bpy.data.scenes["Scene"]
Scene.render.image_settings.file_format = 'PNG'


#Get x- and y-coords for the lower corner in the fourth quadrant
cornerX = targetModel.bound_box[0][0]
cornerY = targetModel.bound_box[0][1]

#Place the model in the first quadrant of the x,y-plane
#dimx = targetModel.dimensions[0]
#dimy = targetModel.dimensions[1]
targetModel.location = mathutils.Vector((-cornerX,-cornerY,0))	

for step in range(0,no_steps):
    #bpy.data.scenes["Scene"].render.filepath = 'C:\CDIO\Tagna_bilder\testbild%d.png' %step
     bpy.ops.render.render( write_still=True)
     image = bpy.data.images['Render Result']
     image.save_render("C:\\CDIO\\Tagna_bilder\\testbild" + str(step) +".png", scene=Scene)