#!/usr/bin/env python
from __future__ import print_function
import os

def jinjaize(template):
    for line in template.splitlines():
        if '{% block' in line:
            print(line)
            end = '{% endblock %}'
        if '{% if' in line:
            print(line)
            end = '{% endif %}'
        if '{% for' in line:
            print(line)
            end = '{% endfor %}'

        if '{% end %}' in line:
            print(line)
            line.replace('{% end %}', end)


def migrate(ext, contents, sep):
    one, two, three = contents.split(sep + '\n')
    media_type = {'txt': 'text/plain', 'html': 'text/html'}[ext]
    return one + '[---]\n' + two + '[---] ' + media_type + '\n' + jinjaize(three)


for path, dirs, files in os.walk('www'):
    for filename in files:
        filepath = os.path.join(path, filename)
        contents = open(filepath).read()
        ext = filepath.rsplit('.', 1)[-1]
        if '/' in ext:
            continue
        if ext in 'acorn ai doc eps gif ico jpg jpeg pdf png psd zip'.split():
            continue

        if '\f' in contents:
            contents = migrate(ext, contents, '\f')
        elif '^L' in contents:
            contents = migrate(ext, contents, '^L')
        else:
            continue

        os.remove(filepath)
        newpath = filepath[:-len(ext)] + 'spt'
        open(newpath, 'w+').write(contents)
