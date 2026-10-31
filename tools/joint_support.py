"""Half-angle support bones reduce arm-joint collapse with glTF skinning."""
import math
import bpy

def add_joint_support(rig,body):
    if 'elbow_support.L' in rig.data.bones:
        return
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    specs=[]
    for side in ('L','R'):
        for label,source,parent,radius,strength in (
            ('elbow','forearm','upper_arm',.18,.8),
            ('shoulder','upper_arm','clavicle',.22,.65)):
            source_name=source+'.'+side
            bone=rig.data.edit_bones[source_name]
            helper=rig.data.edit_bones.new(label+'_support.'+side)
            helper.head=bone.head
            helper.tail=bone.head+(bone.tail-bone.head)*.4
            helper.roll=bone.roll
            helper.parent=rig.data.edit_bones[parent+'.'+side]
            specs.append((helper.name,source_name,parent+'.'+side,helper.head.copy(),radius,strength))
    bpy.ops.object.mode_set(mode='OBJECT')
    for helper,source,parent,center,radius,strength in specs:
        pose=rig.pose.bones[helper]
        constraint=pose.constraints.new('COPY_ROTATION')
        constraint.name='Half-angle joint support'
        constraint.target=rig
        constraint.subtarget=source
        constraint.target_space='LOCAL'
        constraint.owner_space='LOCAL'
        constraint.influence=.5
        group=body.vertex_groups.new(name=helper)
        indices={body.vertex_groups[n].index for n in (source,parent) if n in body.vertex_groups}
        for vertex in body.data.vertices:
            position=body.matrix_world @ vertex.co
            distance=(position-center).length
            if distance>radius*1.6: continue
            blend=strength*math.exp(-((distance/radius)**4))
            weights=[(g.group,g.weight) for g in vertex.groups if g.group in indices]
            total=sum(w for _,w in weights)
            if total<.001: continue
            for index,weight in weights:
                body.vertex_groups[index].add([vertex.index],weight*(1-blend),'REPLACE')
            group.add([vertex.index],total*blend,'REPLACE')
    print('JOINT_SUPPORT',rig.name,len(rig.data.bones),flush=True)

if __name__=='__main__':
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]/'assets/character'
    for name in ('basicMale','basicFemale'):
        bpy.ops.wm.open_mainfile(filepath=str(root/(name+'.blend')))
        rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
        body=bpy.data.objects[name]
        add_joint_support(rig,body)
        bpy.context.scene.frame_set(1)
        bpy.ops.object.select_all(action='DESELECT')
        for o in bpy.context.scene.objects:
            if o.type in {'MESH','ARMATURE'}: o.select_set(True)
        bpy.context.view_layer.objects.active=rig
        bpy.ops.export_scene.gltf(filepath=str(root/(name+'.glb')),use_selection=True,
            export_format='GLB',export_animations=True,export_animation_mode='NLA_TRACKS',
            export_force_sampling=True,export_frame_step=3)
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(root/(name+'.blend')))
