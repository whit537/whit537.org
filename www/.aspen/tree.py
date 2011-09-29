import os

from aspen import resources
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class NotConfigured(Exception):
    pass

# ===========================

def all():
    if _tree is None:
        raise NotConfigured
    posts = _tree.posts[:]
    posts.sort(key=lambda p: p.published)
    posts.reverse()
    return posts

def by_year(only=None):
    posts = all()
    years = []
    for post in posts:
        if only is not None:
            if post.year != only:
                continue
        if not years or (post.year != years[-1][0]):
            years.append([post.year, []])
        years[-1][1].append(post)
    return years


# ===========================

class Post:
    def __init__(self, root, name, published, title, **kw):
        self.root = root
        self.name = name
        self.published = published

        date, time = published.split('T')  
        year, month, day = [int(x) for x in date.split('-')]
        self.year = year
        self.month = month
        self.day = day
        self.title = title

class MockRequest(object):
    def __init__(self, website, parent, name):
        self.website = website
        self.fs = os.path.realpath(os.path.join(parent, name))

class Tree(object): #PatternMatchingEventHandler):

    def __init__(self, website):
        self.website = website
        self.posts = []
        #PatternMatchingEventHandler.__init__(self, ignore_patterns='.*')
        self.prime(website)

    def prime(self, website):
        for parent, dirs, files in os.walk(website.root):
            relparent = parent[len(website.root):]
            if not relparent.startswith('/2'):
                continue
            for name in files:
                mock = MockRequest(website, parent, name)
                resource = resources.load(mock, None)
              
                namespace = { "root": relparent
                            , "name": name
                            , "published": '1970-01-01T00:00.00+0'
                            , "title": 'Untitled'
                             }
                if resource.one is not None:
                    assert isinstance(resource.one, dict) # sanity check
                    namespace.update(resource.one)
                post = Post(**namespace)
                self.posts.append(post)

    def dispatch(self, event):
        import pdb; pdb.set_trace()

_tree = None

def monitor(tree):
    observer = Observer()
    observer.schedule(_tree, path='.', recursive=True)
    observer.start()

def startup(website):
    global _tree
    _tree = Tree(website)
    #monitor(_tree)

def outgoing():
    pass
