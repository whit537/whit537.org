#!/usr/bin/env python
import os
import sys
import xml.parsers.expat

class Post(object):

    published = None
    updated = None
    published = None
    title = ''
    path_parts = None
    content = ''


WANT = ['link', 'published', 'updated', 'title', 'content']
posts = []

class Printer(object):

    cur = None
    indent = 0

    def start(self, name, attrs):
        self.indent += 1
        self.visiting = name
        if name == 'entry':
            self.cur = Post()
        if name == 'link' and 'title' in attrs:
            self.cur.path_parts = attrs['href'][12:].split('/')[1:]
        #print "  " * self.indent, name, attrs.keys()

    def end(self, name):
        self.indent -= 1
        if name == 'entry' and self.cur is not None:
            posts.append(self.cur)

    def chardata(self, data):
        if self.cur is None:
            return
        #print self.visiting
        #data = data.encode('utf-8')
        if self.visiting == 'link':
            self.cur.link = data
        if self.visiting == 'title':
            self.cur.title = data
        if self.visiting == 'published':
            self.cur.published = data
        if self.visiting == 'updated':
            self.cur.updated = data
        if self.visiting == 'content':
            self.cur.content += data



printer = Printer()

p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = printer.start
p.EndElementHandler = printer.end
p.CharacterDataHandler = printer.chardata

p.Parse(sys.stdin.read())

for post in posts:
    year, month, filename = post.path_parts
    if "showComment" in filename:
        continue
    os.system('mkdir -p %s/%s' % (year, month))
    path = '/'.join(post.path_parts)
    print path
    fp = open(path, 'w+')
    for c in post.content:
        if ord(c) > 127:
            print c, ord(c)
            raise SystemExit 

    contents = u"""\
title = "%s"
published = "%s"
updated = "%s"
^L
^L
{%% extends "blag.html" %%}
{%% block content %%}
%s
{%% end %%}
""" % ( post.title.replace('"', r'\"').replace('&', '&amp;')
      , post.published
      , post.updated
      , post.content.replace('^L', '&#94;')
       )
    fp.write(contents.encode('utf-8'))
