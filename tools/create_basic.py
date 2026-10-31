"""Rebuild the approved Basic character, GLB and preview renders."""
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1] / 'assets/character'
FEMALE = '--female' in sys.argv
NAME = 'basicFemale' if FEMALE else 'basicMale'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    p = m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = .72
    out = m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m

skin = material('Warm white vinyl', (.92,.90,.86))
ink = material('Soft charcoal', (.035,.029,.026))
pink = material('Pale peach cheeks', (.94,.65,.55))
parts = []

def sphere(name, center, scale, mat=skin, merge=True):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=40, location=center)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    if merge: parts.append(o)
    return o

def tube(name, rings):
    vertices, faces = [], []
    n = 64
    for j,(x,y,z,rx,ry) in enumerate(rings):
        center=Vector((x,y,z))
        if name=='Arm':
            start=Vector(rings[max(0,j-1)][:3])
            end=Vector(rings[min(len(rings)-1,j+1)][:3])
            tangent=(end-start).normalized()
            depth_axis=Vector((0,1,0))
            radial=depth_axis.cross(tangent).normalized()
            vertices.extend(tuple(center+radial*(rx*math.cos(i*math.tau/n))+depth_axis*(rx*math.sin(i*math.tau/n))) for i in range(n))
        else:
            vertices.extend((x + rx*math.cos(i*math.tau/n),
                             y + ry*math.sin(i*math.tau/n), z) for i in range(n))
    for j in range(len(rings)-1):
        for i in range(n):
            a=j*n+i; b=j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    faces.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))])
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(skin)
    parts.append(o)

# One lofted torso avoids the stacked-sphere abdomen of previous prototypes.
tube('Torso', [(0,0,.96,.025,.025),(0,0,.985,.10,.085),
    (0,0,1.025,.22,.155),(0,0,1.08,.30,.195),(0,0,1.15,.315,.205),
    (0,0,1.25,.31,.205),(0,0,1.45,.29,.205),(0,0,1.66,.31,.205),
    (0,0,1.80,.355,.20),(0,0,1.87,.35,.195),(0,0,1.93,.30,.18),
    (0,0,1.965,.23,.16),(0,0,1.99,.16,.14),(0,0,2.02,.13,.13),
    (0,0,2.12,.13,.125)])
sphere('Oval head',(0,0,2.51),(.46,.355,.48))
for side in (-1,1):
    sphere('Ear',(side*.455,0,2.43),(.075,.085,.115))
    sphere('Soft shoulder',(side*.30,0,1.80),(.125,.14,.13))
    tube('Arm',[(side*.315,0,1.82,.128,.14),
        (side*.39,0,1.72,.128,.14),(side*.44,0,1.62,.125,.137),
        (side*.49,0,1.52,.121,.133),(side*.54,-.002,1.42,.118,.13),
        (side*.59,-.005,1.31,.115,.126),(side*.64,-.01,1.21,.109,.12),
        (side*.69,-.015,1.11,.101,.111)])
    sphere('Mitten palm',(side*.705,-.018,1.065),(.108,.112,.15))
    sphere('Thumb',(side*.635,-.055,1.09),(.052,.06,.09))
    tube('Leg',[(side*.175,0,1.19,.15,.18),
        (side*.195,0,.98,.155,.175),(side*.22,0,.74,.14,.16),
        (side*.25,0,.49,.125,.145),(side*.275,0,.25,.115,.13),
        (side*.28,0,.15,.115,.13)])
    sphere('Rounded foot',(side*.28,-.065,.125),(.155,.235,.125))

bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
body=bpy.context.object
body.name=NAME
body.data.remesh_voxel_size=.012
bpy.ops.object.voxel_remesh()
mod=body.modifiers.new('Smooth joins','SMOOTH')
mod.factor=1
mod.iterations=16
bpy.ops.object.modifier_apply(modifier=mod.name)

# Smooth the curved shoulder loft without imposing a triangular slope.
mod=body.modifiers.new('Polish shoulder silhouette','SMOOTH')
polish_group=body.vertex_groups.new(name='Shoulder polish')
for vertex in body.data.vertices:
    co=body.matrix_world @ vertex.co
    weight=max(0.0,1-abs(co.z-1.78)/.27)*min(1.0,max(0.0,(abs(co.x)-.15)/.10))
    if weight>0: polish_group.add([vertex.index],weight,'REPLACE')
mod.vertex_group=polish_group.name
mod.factor=1
mod.iterations=90
bpy.ops.object.modifier_apply(modifier=mod.name)
for p in body.data.polygons: p.use_smooth=True

group=body.vertex_groups.new(name='Shoulder blending')
for vertex in body.data.vertices:
    co=body.matrix_world @ vertex.co
    weight=max(0.0,1-abs(co.z-1.79)/.25)*min(1.0,max(0.0,(abs(co.x)-.16)/.10))
    if weight>0: group.add([vertex.index],weight,'REPLACE')
mod=body.modifiers.new('Blend shoulder into arm','SMOOTH')
mod.vertex_group=group.name
mod.factor=1.0
mod.iterations=65
bpy.ops.object.modifier_apply(modifier=mod.name)

# Add depth to the torso, blending into the neck and limbs.
inverse = body.matrix_world.inverted()
for vertex in body.data.vertices:
    co = body.matrix_world @ vertex.co
    if co.z < 2.10:
        def ease(t):
            t = max(0.0, min(1.0, t))
            return t*t*(3-2*t)
        neck_weight = ease((2.10 - co.z) / .25)
        foot_weight = ease((co.z - .15) / .30)
        co.y *= 1 + .23 * neck_weight * foot_weight
        vertex.co = inverse @ co
mod=body.modifiers.new('Even surface transitions','SMOOTH')
mod.factor=.7
mod.iterations=8
bpy.ops.object.modifier_apply(modifier=mod.name)

# Increase skull depth while keeping the approved front silhouette.
for vertex in body.data.vertices:
    co = body.matrix_world @ vertex.co
    t = max(0.0, min(1.0, (co.z - 2.04) / .20))
    co.y *= 1 + .25 * t*t*(3-2*t)
    vertex.co = inverse @ co

for side in (-1,1):
    sphere('Oval eye',(side*.18,-.329,2.51),(.037,.022,.060),ink,False)
    sphere('Cheek',(side*.265,-.289,2.39),(.067,.014,.04),pink,False)
sphere('Tiny nose',(0,-.350,2.43),(.034,.038,.031),skin,False)
c=bpy.data.curves.new('Smile','CURVE')
c.dimensions='3D'; c.bevel_depth=.009; c.bevel_resolution=4
s=c.splines.new('BEZIER'); s.bezier_points.add(2)
for p,co in zip(s.bezier_points,[(-.055,-.342,2.36),(0,-.350,2.338),(.055,-.342,2.36)]):
    p.co=co; p.handle_left_type=p.handle_right_type='AUTO'
o=bpy.data.objects.new('Smile',c)
bpy.context.collection.objects.link(o); c.materials.append(ink)
if FEMALE:
    # Subtle body proportions retain the same neutral, simplified toy language.
    inv=body.matrix_world.inverted()
    for vertex in body.data.vertices:
        co=body.matrix_world @ vertex.co
        z=co.z
        waist=math.exp(-((z-1.46)/.20)**2)
        hip=math.exp(-((z-1.08)/.20)**2)
        shoulder=math.exp(-((z-1.84)/.20)**2)
        if z<2.08:
            co.x *= 1-.075*waist+.12*hip-.065*shoulder
            co.y *= 1-.035*waist+.065*hip
            # Broad, modest chest volume with no anatomical surface details.
            chest=math.exp(-((z-1.65)/.155)**2)
            chest_width=math.exp(-((abs(co.x)-.19)/.14)**2)
            front=max(0.0,min(1.0,-co.y/.15))
            upper_chest=math.exp(-((z-1.78)/.18)**2)*math.exp(-(co.x/.26)**4)
            co.y-=(.11*chest*chest_width+.018*upper_chest)*front
            thigh=math.exp(-((z-.86)/.18)**2)
            knee=math.exp(-((z-.61)/.13)**2)
            calf=math.exp(-((z-.42)/.12)**2)
            ankle=math.exp(-((z-.23)/.10)**2)
            leg_factor=1+.025*thigh-.09*knee+.01*calf-.10*ankle
            side=1 if co.x>=0 else -1
            leg_center=side*(.22+(.74-z)*(.055/.49))
            if z<1.16:
                co.x=leg_center+(co.x-leg_center)*leg_factor
                co.y*=leg_factor
                foot=max(0.0,min(1.0,(.24-z)/.12))
                co.x=leg_center+(co.x-leg_center)*(1-.09*foot)
                co.y*=1-.09*foot
            vertex.co=inv @ co
# Raise the female waist and hips, lengthening legs without changing total height.
if FEMALE:
    inv=body.matrix_world.inverted()
    for vertex in body.data.vertices:
        co=body.matrix_world @ vertex.co
        z=co.z
        head_weight=max(0.0,min(1.0,(z-2.00)/.18))
        head_weight=head_weight*head_weight*(3-2*head_weight)
        co.x*=1-.05*head_weight
        co.y*=1-.05*head_weight
        co.z+=(2.51-co.z)*.05*head_weight
        if .15<z<1.96:
            if z<=1.19:
                lift=.09*(z-.15)/(1.19-.15)
            else:
                lift=.09*(1.96-z)/(1.96-1.19)
            co.z+=lift
        vertex.co=inv @ co

# Fill the lateral pelvis transition instead of leaving a narrow hip ridge.
inv=body.matrix_world.inverted()
for vertex in body.data.vertices:
    co=body.matrix_world @ vertex.co
    center=1.20 if FEMALE else 1.13
    envelope=math.exp(-((co.z-center)/.25)**2)
    side_weight=min(1.0,abs(co.x)/.24)**2
    co.x+=(1 if co.x>=0 else -1)*.014*envelope*side_weight
    co.y*=1+.075*envelope
    vertex.co=inv @ co

# Rounded rear pelvis volume, blending into waist and upper thighs.
inv=body.matrix_world.inverted()
for vertex in body.data.vertices:
    co=body.matrix_world @ vertex.co
    center_z=1.17 if FEMALE else 1.10
    vertical=math.exp(-((co.z-center_z)/.27)**2)
    # A broad envelope avoids a crease between two isolated bulges.
    lateral=math.exp(-(co.x/.29)**4)
    t=max(0.0,min(1.0,co.y/.21))
    back=t*t*(3-2*t)
    co.y+=(.065 if FEMALE else .05)*vertical*lateral*back
    vertex.co=inv @ co

rear_group=body.vertex_groups.new(name='Rear pelvis transitions')
for vertex in body.data.vertices:
    co=body.matrix_world @ vertex.co
    weight=math.exp(-((co.z-1.16)/.34)**2)
    if weight>.001: rear_group.add([vertex.index],weight,'REPLACE')
mod=body.modifiers.new('Smooth pelvis into thighs','SMOOTH')
mod.vertex_group=rear_group.name
mod.factor=.8
mod.iterations=90
bpy.ops.object.modifier_apply(modifier=mod.name)

# Remove the flat lower-torso lip and blend the front into the thighs.
groin_group=body.vertex_groups.new(name='Rounded lower pelvis')
inv=body.matrix_world.inverted()
center_z=1.12 if FEMALE else 1.04
for vertex in body.data.vertices:
    co=body.matrix_world @ vertex.co
    weight=math.exp(-((co.z-center_z)/.21)**2)*math.exp(-(co.x/.30)**4)
    if weight>.001: groin_group.add([vertex.index],weight,'REPLACE')
mod=body.modifiers.new('Blend pelvis without horizontal ledge','SMOOTH')
mod.vertex_group=groin_group.name
mod.factor=1
mod.iterations=150
bpy.ops.object.modifier_apply(modifier=mod.name)

# Face attachments follow the deeper skull instead of sinking into its surface.
for obj in bpy.context.scene.objects:
    if obj == body:
        continue
    if obj.type == 'MESH':
        inv = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            co = obj.matrix_world @ vertex.co
            co.y *= 1.25
            if FEMALE:
                co.x*=.95
                co.y*=.95
                co.z=2.51+(co.z-2.51)*.95
            vertex.co = inv @ co
    elif obj.type == 'CURVE':
        for spline in obj.data.splines:
            for point in spline.bezier_points:
                point.co.y *= 1.25
                point.handle_left.y *= 1.25
                point.handle_right.y *= 1.25
                if FEMALE:
                    for attr in ('co','handle_left','handle_right'):
                        value=getattr(point,attr).copy()
                        value.x*=.95
                        value.y*=.95
                        value.z=2.51+(value.z-2.51)*.95
                        setattr(point,attr,value)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT/f'{NAME}.glb'),use_selection=True,export_format='GLB')

scene=bpy.context.scene
scene.world=bpy.data.worlds.new('Soft studio')
scene.world.use_nodes=True
nt=scene.world.node_tree
nt.nodes.clear()
bg=nt.nodes.new('ShaderNodeBackground'); bg.inputs['Color'].default_value=(.75,.73,.69,1)
bg.inputs['Strength'].default_value=.5
wo=nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(bg.outputs[0],wo.inputs[0])
for name,loc,power,size in [('Key',(-3,-4,5),380,4),('Fill',(3,-3,3),180,4),('Rim',(2,3,4),300,3)]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.size=size
    o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
bpy.context.collection.objects.link(cam)
cam.data.type='ORTHO'; cam.data.ortho_scale=3.5
scene.camera=cam
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=850; scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.film_transparent=True
for view,location in [('front',(0,-8,1.5)),('side',(8,0,1.5)),('three-quarter',(3,-8,2.4)),('back',(0,8,1.5)),('rear-quarter',(3,8,2.4))]:
    cam.location=location
    cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/f'{NAME}-{view}.png')
    bpy.ops.render.render(write_still=True)
cam.location=(0,-8,1.5)
cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{NAME}.blend'))
