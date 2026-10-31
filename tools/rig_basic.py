"""Add a prototype humanoid rig and looping movement to approved base meshes."""
import bpy
import runpy
import sys
from pathlib import Path
from math import radians, sqrt
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]/'assets/character'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_motion import add_run_bounce
from joint_support import add_joint_support
from arm_deformation import configure_arm_volume, arm_test_actions
for name in ('basicMale','basicFemale'):
    # Always rebuild the unrigged base first to avoid stacking rigs on reruns.
    sys.argv=['create_basic.py']+(['--female'] if name=='basicFemale' else [])
    runpy.run_path(str(Path(__file__).with_name('create_basic.py')),run_name='__main__')
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/(name+'.blend')))
    scene=bpy.context.scene
    body=bpy.data.objects[name]
    meshes=[o for o in scene.objects if o.type in {'MESH','CURVE'}]
    bpy.ops.object.select_all(action='DESELECT')
    arm=bpy.data.armatures.new(name+'Skeleton')
    rig=bpy.data.objects.new(name+'Rig',arm)
    scene.collection.objects.link(rig)
    rig.show_in_front=True
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    definitions=[('root',(0,0,.12),(0,0,.8),None),
        ('hips',(0,0,.95),(0,0,1.20),'root'),
        ('spine',(0,0,1.20),(0,0,1.60),'hips'),
        ('chest',(0,0,1.60),(0,0,1.93),'spine'),
        ('neck',(0,0,1.93),(0,0,2.10),'chest'),
        ('head',(0,0,2.10),(0,0,2.84),'neck')]
    for side,suffix in ((1,'L'),(-1,'R')):
        definitions.extend([
            ('clavicle.'+suffix,(0,0,1.91),(side*.32,0,1.90),'chest'),
            ('upper_arm.'+suffix,(side*.32,0,1.90),(side*.50,0,1.49),'clavicle.'+suffix),
            ('forearm.'+suffix,(side*.50,0,1.49),(side*.68,-.01,1.13),'upper_arm.'+suffix),
            ('hand.'+suffix,(side*.68,-.01,1.13),(side*.71,-.02,.98),'forearm.'+suffix),
            ('thigh.'+suffix,(side*.17,0,1.10),(side*.235,0,.62),'hips'),
            ('shin.'+suffix,(side*.235,0,.62),(side*.28,0,.20),'thigh.'+suffix),
            ('foot.'+suffix,(side*.28,0,.20),(side*.28,-.22,.10),'shin.'+suffix)])
    for bone_name,head,tail,parent in definitions:
        bone=arm.edit_bones.new(bone_name)
        bone.head=head; bone.tail=tail
        if parent: bone.parent=arm.edit_bones[parent]
        if bone_name=='root': bone.use_deform=False
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    # Replace diffuse heat weights on the arm with a smooth longitudinal blend.
    for side,sign in (('L',1),('R',-1)):
        upper=rig.data.bones['upper_arm.'+side]
        fore=rig.data.bones['forearm.'+side]
        start=upper.head_local
        axis=(fore.tail_local-start).normalized()
        elbow_distance=(upper.tail_local-start).dot(axis)
        wrist_distance=(fore.tail_local-start).dot(axis)
        def ease(t):
            t=max(0,min(1,t)); return t*t*(3-2*t)
        for v in body.data.vertices:
            co=body.matrix_world @ v.co
            # Below the armpit the torso must never follow the arm chain.
            if abs(co.x)<.37 and 1.08<co.z<1.57:
                arm_groups=[g for g in list(v.groups) if any(k in body.vertex_groups[g.group].name for k in ('upper_arm','forearm','hand','clavicle'))]
                transition=ease((.37-abs(co.x))/.14)*ease((co.z-1.08)/.15)*ease((1.57-co.z)/.20)
                removed=sum(g.weight for g in arm_groups)*transition
                for g in arm_groups: body.vertex_groups[g.group].add([v.index],g.weight*(1-transition),'REPLACE')
                if removed:
                    target=body.vertex_groups['spine']
                    existing=next((g.weight for g in v.groups if g.group==target.index),0)
                    target.add([v.index],existing+removed,'REPLACE')
            if sign*co.x<.30 or not 1.02<co.z<1.98: continue
            distance=(co-start).dot(axis)
            radial_distance=(co-(start+axis*distance)).length
            if radial_distance>.23: continue
            blend=ease((sign*co.x-.30)/.14)*ease((.23-radial_distance)/.07)*ease((co.z-1.02)/.13)*ease((1.98-co.z)/.14)
            shoulder=ease(distance/.20)
            bend=ease((distance-elbow_distance+.11)/.22)
            hand=ease((distance-wrist_distance+.055)/.12)
            weights={'clavicle.'+side:1-shoulder,'upper_arm.'+side:shoulder*(1-bend),
                'forearm.'+side:shoulder*bend*(1-hand),'hand.'+side:shoulder*bend*hand}
            old={body.vertex_groups[g.group].name:g.weight for g in v.groups}
            for key in old.keys()|weights.keys():
                value=old.get(key,0)*(1-blend)+weights.get(key,0)*blend
                body.vertex_groups[key].add([v.index],value,'REPLACE')
    add_joint_support(rig,body)
    configure_arm_volume(rig)
    # Rigid head attachments keep facial features aligned during head movement.
    for obj in meshes:
        if obj==body: continue
        if obj.type=='CURVE':
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True); bpy.context.view_layer.objects.active=obj
            bpy.ops.object.convert(target='MESH')
            obj=bpy.context.object
        group=obj.vertex_groups.new(name='head')
        group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
        mod=obj.modifiers.new('Follow head','ARMATURE'); mod.object=rig
        obj.parent=rig
    scene.frame_start=1; scene.frame_end=120
    scene.render.fps=30
    for pose in rig.pose.bones: pose.rotation_mode='XYZ'
    for frame,lift in ((1,0),(30,1),(60,0),(90,-.20),(120,0)):
        for pose in rig.pose.bones: pose.rotation_euler=(0,0,0)
        rig.pose.bones['chest'].scale=(1+.012*lift,1+.025*lift,1+.008*lift)
        rig.pose.bones['head'].rotation_euler.y=radians(4)*lift
        rig.pose.bones['upper_arm.L'].rotation_euler.z=radians(-18)*lift
        rig.pose.bones['forearm.L'].rotation_euler.x=radians(-25)*lift
        rig.pose.bones['upper_arm.R'].rotation_euler.z=radians(8)*lift
        for pose in rig.pose.bones:
            pose.keyframe_insert(data_path='rotation_euler',frame=frame,group=pose.name)
        rig.pose.bones['chest'].keyframe_insert(data_path='scale',frame=frame)
    if rig.animation_data and rig.animation_data.action:
        rig.animation_data.action.name='BasicMovementTest'
    test_action=rig.animation_data.action
    rig.animation_data.action=None
    clips=[('BasicMovementTest',test_action)]
    for clip_name,period in [('BreathingIdle',60),('BreathingRecovery',30)]:
        rig.animation_data.action=None
        for pose in rig.pose.bones:
            pose.rotation_euler=(0,0,0)
            pose.scale=(1,1,1)
        for frame,amount in [(1,0),(1+period//2,1),(1+period,0)]:
            chest=rig.pose.bones['chest']
            chest.scale=(1+.012*amount,1+.025*amount,1+.008*amount)
            chest.keyframe_insert(data_path='scale',frame=frame,group='chest')
        action=rig.animation_data.action
        action.name=clip_name
        clips.append((clip_name,action))
    # Prototype gestures, all returning to the same neutral pose.
    for clip_name,period in [('Flex',90),('WipeSweat',90),('Run',30)]:
        rig.animation_data.action=None
        frames=[1,16,31] if clip_name=='Run' else [1,23,46,68,91]
        for index,frame in enumerate(frames):
            for pose in rig.pose.bones:
                pose.rotation_euler=(0,0,0)
                pose.scale=(1,1,1)
                pose.location=(0,0,0)
            amount=[0,1,1,1,0][index] if clip_name!='Run' else [1,-1,1][index]
            def rotate(bone,x=0,y=0,z=0):
                rig.pose.bones[bone].rotation_euler=tuple(radians(v) for v in (x,y,z))
            if clip_name=='Flex':
                rotate('upper_arm.L',0,0,-80*amount)
                rotate('upper_arm.R',0,0,80*amount)
                rotate('forearm.L',-5*amount,0,-75*amount)
                rotate('forearm.R',-5*amount,0,75*amount)
                rotate('chest',-4*amount)
            elif clip_name=='WipeSweat':
                rotate('head',0,-6*amount,-4*amount)
                if amount:
                    bpy.context.view_layer.update()
                    upper=rig.pose.bones['upper_arm.L']
                    fore=rig.pose.bones['forearm.L']
                    start=upper.head.copy()
                    target=Vector((.12 if index==2 else .28,-.57,2.33))
                    direction=target-start
                    distance=direction.length
                    unit=direction.normalized()
                    l1=upper.bone.length; l2=fore.bone.length
                    along=(l1*l1-l2*l2+distance*distance)/(2*distance)
                    height=sqrt(max(0,l1*l1-along*along))
                    outward=Vector((1,0,0))
                    outward=(outward-unit*outward.dot(unit)).normalized()
                    elbow=start+unit*along+outward*height
                    upper.matrix=Matrix.LocRotScale(start,(elbow-start).to_track_quat('Y','Z'),Vector((1,1,1)))
                    bpy.context.view_layer.update()
                    fore.matrix=Matrix.LocRotScale(fore.head.copy(),(target-fore.head).to_track_quat('Y','Z'),Vector((1,1,1)))
                    bpy.context.view_layer.update()
            else:
                rotate('thigh.L',50*amount)
                rotate('thigh.R',-50*amount)
                rotate('shin.L',max(0,amount)*95)
                rotate('shin.R',max(0,-amount)*95)
                rotate('foot.L',-15*amount)
                rotate('foot.R',15*amount)
                rotate('upper_arm.L',-45*amount)
                rotate('upper_arm.R',45*amount)
                rotate('forearm.L',-90)
                rotate('forearm.R',-90)
                rotate('chest',12)
            for pose in rig.pose.bones:
                pose.keyframe_insert(data_path='rotation_euler',frame=frame,group=pose.name)
                pose.keyframe_insert(data_path='scale',frame=frame,group=pose.name)
                pose.keyframe_insert(data_path='location',frame=frame,group=pose.name)
        action=rig.animation_data.action
        action.name=clip_name
        if clip_name=='Run': add_run_bounce(rig,action)
        clips.append((clip_name,action))
    rig.animation_data.action=None
    clips.extend(arm_test_actions(rig))
    for pose in rig.pose.bones:
        pose.rotation_euler=(0,0,0)
        pose.location=(0,0,0)
        pose.scale=(1,1,1)
    for clip_name,action in clips:
        track=rig.animation_data.nla_tracks.new()
        track.name=clip_name
        strip=track.strips.new(clip_name,1,action)
        track.mute=True
    # Preview the normal breathing clip, repeated across the timeline.
    idle_track=next(t for t in rig.animation_data.nla_tracks if t.name=='BreathingIdle')
    idle_track.mute=False
    idle_track.strips[0].repeat=2
    scene.frame_end=120
    scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in {'MESH','ARMATURE'}: obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(ROOT/(name+'.glb')),
        use_selection=True,export_format='GLB',export_animations=True,
        export_animation_mode='NLA_TRACKS',export_force_sampling=False,export_frame_step=3)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(name+'.blend')))
    scene.frame_set(30)
    scene.render.filepath='/private/tmp/'+name+'-rig-test.png'
    bpy.ops.render.render(write_still=True)
    print('RIGGED',name,'bones',len(arm.bones),'weighted_vertices',len(body.data.vertices))
    for preview in ROOT.glob(name+'-*.png'):
        preview.unlink()
