"""Shared vertical motion for the prototype Run clip."""
def add_run_bounce(rig, action):
    previous=rig.animation_data.action
    use_nla=rig.animation_data.use_nla
    rig.animation_data.use_nla=False
    rig.animation_data.action=action
    root=rig.pose.bones['root']
    # Root's local Y points upward in world space. Two steps per stride.
    for frame,height in ((1,0),(8,.065),(16,0),(23,.065),(31,0)):
        root.location=(0,height,0)
        root.keyframe_insert(data_path='location',frame=frame,group='root')
    root.location=(0,0,0)
    rig.animation_data.action=previous
    rig.animation_data.use_nla=use_nla
