import json; d=json.load(open('rata_data.json'))
d['bdSkip']=[[-695.49,-724.01],[-697.89,-726.46],[-549.78,-1086.07],[-526.65,-1098.43]]
d['silta']=[x for x in json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__) or '.', 'silta.json'))) if x['a'][0] < 0]
d['portal']={'x':-427.5,'y':-1003.6,'dx':0.741,'dy':0.672,'w':5.2}
d['glass']=[[-448.0,-1009.5,15.0,3.0],[-426.8,-990.5,5.5,3.6]]
d['hideB']=[2298,2299]
open(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', '..', 'rata', 'rata_data.js'),'w').write('// Porin rataverkko (OSM 20.11.2026, juna/build/build_data.py) – älä muokkaa käsin\nexport default '+json.dumps(d,separators=(',',':'))+';\n')
