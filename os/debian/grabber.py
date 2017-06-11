import re
import os
import requests
import json

versions = ["jessie", "wheezy"]

for v in versions:
    lst = []
    r = requests.get('https://packages.debian.org/'+v+'/allpackages')
    kek = r.text.split('\n')
    for idx, k in enumerate(kek):
        if idx < 6:
            continue
        tmp = k.split()
        lst.append({"name":tmp[0], "version": tmp[1]})
    if not os.path.exists(v):
        os.makedirs(v)
    with open(v+'/packages.json', 'w') as file:
        json.dump(lst, file, indent=4, sort_keys=True)
    file.close()