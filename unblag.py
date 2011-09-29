#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

p.Parse(open('blag.bak/blag.xml').read())

blaps = [ (unichr(8217), '&rsquo;')
        , (unichr(8211), '&mdash;') # should have been
        , (unichr(8212), '&mdash;')
        , (unichr(8220), '&ldquo;')
        , (unichr(8221), '&rdquo;')
        , (unichr(233), '&eacute;')
        , (unichr(8230), '&hellip;')
        , (unichr(160), '')         # &nbsp; 
        , (unichr(8482), '&trade;') 
        , (unichr(960), '&pi;')
        , (unichr(230), '&#xe6;')   # æ
        , (unichr(234), '&#xea;')   # ê
        , (unichr(239), '&#xef;')   # ï
        , (unichr(241), '&#xf1;')   # ñ
        , (unichr(246), '&#xf6;')   # ö
        , (unichr(347), '&#015b;')  # ś
        , (unichr(252), '&#xfc;')   # ü
         ]

seen = set()

for post in posts:
    year, month, filename = post.path_parts
    if "showComment" in filename:
        continue
    os.system('mkdir -p www/%s/%s' % (year, month))
    path = '/'.join(['www'] + post.path_parts)
    fp = open(path, 'w+')

    for blip, blop in blaps:
        post.content = post.content.replace(blip, blop)

    for c in post.content:
        if ord(c) > 127:
            seen.add(c)
            print c, str(ord(c)).rjust(4), path

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

for c in seen:
    pass
    #print ord(c), repr(unichr(ord(c))), c
