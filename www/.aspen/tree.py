import os
import os.path

import pymongo
import pymongo.uri_parser
from aspen import resources


class MockRequest(object):
    def __init__(self, website, path):
        website.copy_configuration_to(self)
        self.website = website
        self.fs = path

def Database():
    connect = os.environ['MONGO']
    conn = pymongo.Connection(connect)

    # grab the dbname, because we can't get it via the Connection
    dbname = pymongo.uri_parser.parse_uri(connect)["database"]

    return conn[dbname]

class File(dict):
    def __getattr__(self, name):
        try:
            return dict.__getitem__
        except KeyError:
            raise AttributeError("No attribute named %s.")

db = None
def startup(website):
    global db
    _db = Database()
    _db.drop_collection('tree')
    db = _db['tree']

    for path, dirs, files in os.walk(website.root):

        # Ignore hidden files.
        # ====================

        for seq in (dirs, files):
            for i in range(len(dirs)-1, -1, -1):
                name = dirs[i]
                if name.startswith('.'):
                    dirs.pop(i)

        # Index files.
        # ============

        parent = path[len(website.root):].replace(os.sep, '/')
        for name in files:
            mock = MockRequest(website, os.path.join(path, name))
            resource = resources.load(mock, modtime=None)

            doc = {"_id": '/'.join([parent, name])}
            if hasattr(resource, 'one'):
                assert isinstance(resource.one, dict) # sanity check
                for k, v in resource.one.items():
                    if isinstance(v, (basestring,)):
                        doc[k] = v

            db.save(doc)
