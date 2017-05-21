import re
import os
import requests
import json

versions = ["trusty", "xenial"]

for v in versions:
    r = requests.get('http://packages.ubuntu.com/ru/'+v+'/allpackages')
    pattern = re.compile("<dt><a href='[^>]+>(?P<name>.+)</a> \((?P<version>[^\)]+).+<strong.*?>(?P<type>.+?)</strong>\]")
    kek = [m.groupdict() for m in pattern.finditer(r.text)]
    
    if not os.path.exists(v):
        os.makedirs(v)
    with open(v+'/packages.json', 'w') as file:
        json.dump(kek, file, indent=4, sort_keys=True)
    file.close()