#! /usr/bin/env python3

import toml
import json

with open('test.toml','r') as f:
    obj = toml.load(f)


print(json.dumps(obj,indent=4))

