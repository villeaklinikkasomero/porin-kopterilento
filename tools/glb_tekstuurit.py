# GLB:n upotetut tekstuurit pienemmiksi (Meshyn 2048 px JPEG:t -> 512 px värikartta ja normaali, 256 px muut). Geometria ennallaan.
# usage: python3 tools/glb_tekstuurit.py lahde.glb kohde.glb
import struct, json, io, sys, base64
from PIL import Image
def repack(src, dst, size_base=512, size_other=256):
    b=open(src,'rb').read(); L=struct.unpack('<I',b[12:16])[0]; J=json.loads(b[20:20+L])
    off=20+L; BL=struct.unpack('<I',b[off:off+4])[0]; BIN=b[off+8:off+8+BL]
    mat=J['materials'][0]; texrole={}
    pbr=mat.get('pbrMetallicRoughness',{})
    if 'baseColorTexture' in pbr: texrole[J['textures'][pbr['baseColorTexture']['index']]['source']]='base'
    for k in ('normalTexture',): 
        if k in mat: texrole[J['textures'][mat[k]['index']]['source']]='normal'
    if 'metallicRoughnessTexture' in pbr: texrole[J['textures'][pbr['metallicRoughnessTexture']['index']]['source']]='mr'
    newbin=bytearray(); views=[]
    # rebuild bufferViews: copy non-image views, replace image views
    imgview={im['bufferView']:i for i,im in enumerate(J.get('images',[]))}
    for vi,v in enumerate(J['bufferViews']):
        data=BIN[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
        if vi in imgview:
            role=texrole.get(imgview[vi],'other'); im=Image.open(io.BytesIO(data)).convert('RGB')
            s=size_base if role in ('base','normal') else size_other; im=im.resize((s,s),Image.LANCZOS)
            o=io.BytesIO(); im.save(o,'JPEG',quality=88 if role!='normal' else 92); data=o.getvalue()
            J['images'][imgview[vi]]['mimeType']='image/jpeg'
        while len(newbin)%4: newbin.append(0)
        v['byteOffset']=len(newbin); v['byteLength']=len(data); newbin+=data
    while len(newbin)%4: newbin.append(0)
    J['buffers'][0]['byteLength']=len(newbin)
    js=json.dumps(J,separators=(',',':')).encode(); 
    while len(js)%4: js+=b' '
    out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(newbin))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(newbin),0x004E4942)+bytes(newbin)
    open(dst,'wb').write(out); print(dst,len(out),texrole)
repack(sys.argv[1],sys.argv[2])
