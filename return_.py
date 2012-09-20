import os
import subprocess
import threading
import urllib

from aspen.utils import to_age

BASE = os.path.realpath(os.path.dirname(__file__))
BIN = "%s/return/return" % BASE
DAT = "%s/return/return.dat" % BASE
LOG = "%s/return/return.log" % BASE
BAD = "%s/return/bad-words.txt" % BASE


def getoutput(*cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return proc.communicate()[0]


lock = threading.Lock()
def do(cmd):
    with lock:
        return getoutput(BIN, DAT, LOG, cmd)


def future():
    items = do("future").splitlines()
    for item in items:
        votes, ts_created, query = item.split(',', 2)
        age = to_age(float(ts_created))
        escaped = urllib.quote_plus(query)
        yield (votes, age, query, escaped)

def past():
    nfuture = len(do("future").splitlines())
    npast = 21 - nfuture
    raw = getoutput("tail", "-n%d" % npast, LOG)
    i = 0
    for line in reversed(raw.splitlines()):
        votes, ts_created, ts_posted, query = line.split(',', 3)
        age = to_age(float(ts_posted))
        if i == 0:
            if age.startswith("1 "):
                age = age.split()[1]
        yield (votes, age, query)
        i += 1

