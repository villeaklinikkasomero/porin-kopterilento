"""Cycles on the GPU when PORI_GPU=1 (AWS Batch GPU instances). OptiX first, then CUDA; CPU otherwise."""
import os


def enable(scene):
    if os.environ.get('PORI_GPU') != '1': return 'CPU'
    import bpy
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for kind in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = kind; prefs.get_devices()
            devs = [d for d in prefs.devices if d.type == kind]
            if not devs: continue
            for d in prefs.devices: d.use = d.type == kind
            scene.cycles.device = 'GPU'; print('cycles on', kind, [d.name for d in devs]); return kind
        except Exception as e:
            print('gpu', kind, 'not available:', e)
    return 'CPU'
