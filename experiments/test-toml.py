#! /usr/bin/env python3

import toml

def load_toml_config(filepath, clean=True):
    with open(filepath,'r') as f:
        obj = toml.load(f)

    for src in obj['sources']:
        print(src)
        if 'sources__ARR' in src:
            lst = []
            for l in src['sources__ARR'].splitlines():
                l = l.strip()
                if l != '' and not l.startswith('#'):
                    lst.append(l)
            src['sources'] = lst
            if clean:
                del src['sources__ARR']
    return obj

if __name__ == '__main__':
    fp = 'test.toml'
    obj = load_toml_config(fp)
    import json
    print(json.dumps(obj,indent=4))

