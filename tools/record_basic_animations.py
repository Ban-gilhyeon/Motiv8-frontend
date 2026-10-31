"""Record each character's three NLA clips as separate MP4 previews."""
from pathlib import Path
import bpy
import sys
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/character-previews'
OUT.mkdir(parents=True,exist_ok=True)
for name in ('basicMale','basicFemale'):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/character'/(name+'.blend')))
    scene=bpy.context.scene
    rig=next(o for o in scene.objects if o.type=='ARMATURE')
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD'
    scene.world.color=(.14,.16,.18)
    scene.render.film_transparent=False
    scene.render.resolution_x=480
    scene.render.resolution_y=600
    scene.render.resolution_percentage=100
    scene.render.fps=15
    scene.frame_start=1; scene.frame_end=120; scene.frame_step=2
    scene.render.image_settings.media_type='VIDEO'
    scene.render.image_settings.file_format='FFMPEG'
    scene.render.ffmpeg.format='MPEG4'
    scene.render.ffmpeg.codec='H264'
    scene.render.ffmpeg.constant_rate_factor='MEDIUM'
    scene.camera.location=(2.8,-8,2.1)
    scene.camera.rotation_euler=(Vector((0,0,1.5))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    for clip in (('ShoulderRangeTest','ElbowVolumeTest') if '--joint-tests' in sys.argv else ('Flex',) if '--flex-only' in sys.argv else ('Run',) if '--run-only' in sys.argv else ('Flex','WipeSweat','Run')):
        scene.frame_end=180 if '--joint-tests' in sys.argv else 120
        for track in rig.animation_data.nla_tracks:
            track.mute=track.name!=clip
            strip=track.strips[0]
            period=strip.action.frame_range[1]-strip.action.frame_range[0]
            strip.repeat=scene.frame_end/period
        for pose in rig.pose.bones:
            pose.rotation_euler=(0,0,0)
            pose.scale=(1,1,1)
        scene.frame_set(1)
        scene.render.filepath=str(OUT/(name+'-'+clip+'.mp4'))
        # Compare sampled evaluated surfaces to detect frozen clips or invalid deformation.
        body=bpy.data.objects[name]
        samples=[]
        for frame in (1,8,16,31):
            scene.frame_set(frame)
            evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
            mesh=evaluated.to_mesh()
            samples.append([v.co.copy() for v in mesh.vertices])
            evaluated.to_mesh_clear()
        maximum=max((a-b).length for sample in samples[1:] for a,b in zip(samples[0],sample))
        assert maximum>1e-5,(name,clip,'no movement')
        print('VERIFIED_MOVEMENT',name,clip,maximum,flush=True)
        video_path=scene.render.filepath
        scene.frame_set(16 if clip=='Run' else 46)
        scene.render.image_settings.media_type='IMAGE'
        scene.render.image_settings.file_format='PNG'
        scene.render.filepath='/private/tmp/'+name+'-'+clip+'-pose.png'
        bpy.ops.render.render(write_still=True)
        scene.render.image_settings.media_type='VIDEO'
        scene.render.image_settings.file_format='FFMPEG'
        scene.render.filepath=video_path
        scene.frame_set(1)
        bpy.ops.render.render(animation=True)
        print('RECORDED',scene.render.filepath,flush=True)
