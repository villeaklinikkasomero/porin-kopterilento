import json,sys
V=json.load(open('views.json')); a,b=int(sys.argv[1]),int(sys.argv[2]); sv=len(sys.argv)<4
A=[]
for v in V[a:b]:
    A+=[{"name":"javascript_tool","input":{"tabId":"tab-2","action":"javascript_exec","text":f"await window.__shot({v['x']},{v['y']},{v['h']}); '{v['k']}'"}},
        {"name":"computer","input":{"tabId":"tab-2","action":"screenshot","scale":0.5}}]
    if sv: A+=[{"name":"tabs_select","input":{"tabId":"seed"}},
        {"name":"navigate","input":{"tabId":"seed","url":f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={v['lat']},{v['lon']}&heading={v['h']}&pitch=12&fov=90"}},
        {"name":"computer","input":{"tabId":"seed","action":"wait","duration":6}},
        {"name":"computer","input":{"tabId":"seed","action":"screenshot","scale":0.5}}]
print(json.dumps(A))
