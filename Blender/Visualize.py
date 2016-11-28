'''
Render a camera in the model at specified coordinates
'''
import bpy, math

#Start of setup-------------------------------------------------------------------------------

xpos = 153
ypos = 98
zpos = 1.94
xrot = 90
yrot = 0.54
zrot = 78.2

#End of setup---------------------------------------------------------------------------------

bpy.ops.mesh.primitive_cone_add(location=(0,0,0),rotation = (math.radians(90),math.radians(45),math.radians(-90)),vertices = 4,radius1 = 1.2, radius2 = 0)
part1 = bpy.context.selected_objects
bpy.ops.mesh.primitive_cube_add(location=(-1,0,0))
part1[0].select = True
bpy.ops.object.join()
cameraIndicator = bpy.context.selected_objects[0]

cameraIndicator.location = (xpos,ypos,zpos)
cameraIndicator.rotation_euler = (math.radians(xrot),math.radians(yrot),math.radians(zrot+90))



