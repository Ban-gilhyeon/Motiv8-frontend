"""Volume-compensated support bones and isolated arm range-of-motion tests."""
import math
import bpy

def configure_arm_volume(rig):
    for side in ('L','R'):
        for label,source,limit in (('elbow','forearm',1.4),('shoulder','upper_arm',1.28)):
            pose=rig.pose.bones[label+'_support.'+side]
            for axis in (0,2):
                pose.driver_remove('scale',axis)
                driver=pose.driver_add('scale',axis).driver
                for component in ('X','Y','Z'):
                    variable=driver.variables.new()
                    variable.name='r'+component.lower()
                    variable.type='TRANSFORMS'
                    target=variable.targets[0]
                    target.id=rig
                    target.bone_target=source+'.'+side
                    target.transform_type='ROT_'+component
                    target.transform_space='LOCAL_SPACE'
                driver.expression=f'min({limit},1/max(0.6,cos(min(2.6,sqrt(rx*rx+ry*ry+rz*rz))*0.5)))'

def arm_test_actions(rig):
    previous=rig.animation_data.action
    old_nla=rig.animation_data.use_nla
    rig.animation_data.use_nla=False
    clips=[]
    tests={
        'ShoulderRangeTest':[(0,0,0),(0,0,-90),(-90,0,0),(0,60,-110),(45,-45,-60),(0,0,-140),(0,0,0)],
        'ElbowVolumeTest':[0,45,90,120,145,90,0],
    }
    for name,poses in tests.items():
        rig.animation_data.action=None
        for index,values in enumerate(poses):
            frame=1+index*30
            for pose in rig.pose.bones:
                pose.rotation_mode='XYZ'
                pose.rotation_euler=(0,0,0)
                pose.location=(0,0,0)
                pose.scale=(1,1,1)
            for side,sign in (('L',-1),('R',1)):
                if name=='ShoulderRangeTest':
                    x,y,z=values
                    rig.pose.bones['upper_arm.'+side].rotation_euler=tuple(math.radians(a) for a in (x,y if side=='L' else -y,z if side=='L' else -z))
                    # Raising an arm includes clavicle motion, rather than rotating only the socket.
                    rig.pose.bones['clavicle.'+side].rotation_euler.z=math.radians(sign*max(0,abs(z)-60)*.22)
                else:
                    rig.pose.bones['upper_arm.'+side].rotation_euler.z=math.radians(sign*45)
                    rig.pose.bones['forearm.'+side].rotation_euler.z=math.radians(sign*values)
            for pose in rig.pose.bones:
                pose.keyframe_insert(data_path='rotation_euler',frame=frame,group=pose.name)
                pose.keyframe_insert(data_path='location',frame=frame,group=pose.name)
        action=rig.animation_data.action
        action.name=name
        clips.append((name,action))
    rig.animation_data.action=previous
    rig.animation_data.use_nla=old_nla
    return clips

if __name__=='__main__':
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]/'assets/character'
    for name in ('basicMale','basicFemale'):
        bpy.ops.wm.open_mainfile(filepath=str(root/(name+'.blend')))
        rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
        configure_arm_volume(rig)
        for clip,action in arm_test_actions(rig):
            track=rig.animation_data.nla_tracks.new(); track.name=clip
            track.strips.new(clip,1,action); track.mute=True
        for pose in rig.pose.bones:
            pose.rotation_euler=(0,0,0); pose.location=(0,0,0); pose.scale=(1,1,1)
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
