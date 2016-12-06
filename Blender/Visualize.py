'''
Render a camera in the model at specified coordinates
'''
import bpy, math
from mathutils import Vector

#Start of setup-------------------------------------------------------------------------------

xpos = 220
ypos = 60
tilt = -20
angle = 30
cameraHeight = 4
targetModelName = "teknikringen8"

#End of setup---------------------------------------------------------------------------------

targetModel = bpy.data.objects[targetModelName]

bpy.ops.mesh.primitive_cone_add(location=(0,0,0),rotation = (math.radians(90),math.radians(45),math.radians(-90)),vertices = 4,radius1 = 1.2, radius2 = 0)
part1 = bpy.context.selected_objects
bpy.ops.mesh.primitive_cube_add(location=(-1,0,0))
part1[0].select = True
bpy.ops.object.join()
cameraIndicator = bpy.context.selected_objects[0]

#Place camera in desired location and put at correct height over the ground
bpy.context.scene.objects.active = cameraIndicator
bpy.context.active_object.location = [xpos,ypos,0]
localCameraObject = targetModel.matrix_world.inverted()*Vector((xpos,ypos,0))
depthCast = targetModel.ray_cast([localCameraObject[0],localCameraObject[1],100],[0,0,-1])
depthCastGlobal = targetModel.matrix_world*depthCast[1]

cameraIndicator.location = (xpos,ypos,depthCastGlobal[2] + cameraHeight)
cameraIndicator.rotation_euler = (math.radians(tilt),math.radians(0),math.radians(angle+90))



