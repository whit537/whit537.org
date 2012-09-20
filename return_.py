import os
import subprocess
import threading
import urllib

from aspen.utils import to_age, utc

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

def future():
    for item in []:
        yield  # fossilized

def past():
    nfuture = len(do("future").splitlines())
    npast = 21 - nfuture
    raw = getoutput("tail", "-n%d" % npast, LOG)
    i = 0
    for line in reversed(raw.splitlines()):
        votes, ts_created, ts_posted, query = line.split(',', 3)
        age = to_age(datetime.datetime.fromtimestamp(float(ts_posted)))
        if i == 0:
            if age.startswith("1 "):
                age = age.split()[1]
        yield (votes, age, query)
        i += 1

PAST = """\
1,1260567565.662045,1260567588.66938,Hello?
1,1260567709.402118,1260567712.217441,BLAM!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
42,1260567712.356303,1260567748.844182,BLAM!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
1,1260567901.276421,1260567907.463529,Oh man.
1,1260567966.232787,1260567969.833573,Again?
1,1260567977.102392,1260568001.323973,Oh man.
1,1260568047.360930,1260568062.730082,Only hot.
1,1260568134.90555,1260568154.327818,YOU ROCK!!!!!!!!!!!!
1,1260568988.450111,1260569001.337559,welcome to the hallway
1,1260569022.139204,1260569033.952002,From the road. :-)
2,1260569034.258251,1260569066.224010,From the road. :-)
1,1260569133.584200,1260569158.732124,Hallway! Thank you! :-D
3,1260570102.950720,1260570126.22271,meditation
1,1260570277.307851,1260570277.817692,love
1,1260570306.887364,1260570308.561295,love
2,1260586165.880086,1260667071.239403,BTW, click on me to upvote.
1,1260586087.285081,1260667105.77358,I went to HackPGH tonight.
1,1260586096.401486,1260667138.252973,It was humbling.
1,1260586117.806686,1260667170.237294,I do not understand electricity.
1,1260586124.799065,1260667203.807373,I do not understand magnetism.
1,1260586146.121603,1260667237.187799,Short of understanding, use even.
1,1260587102.755447,1260667270.856333,most boast coast roast ghost
1,1260587129.203061,1260667303.984952,Also, this should be a realtime app.
1,1260587138.737721,1260667338.1485,Realtime is hard, I am realizing.
1,1260587144.353672,1260667371.748568,I wonder what AppJet looks like?
1,1260667096.205597,1260667405.525025,Hoy`n`cold
1,1260667373.604212,1260667436.890730,love story
1,1260667445.334742,1260667468.205140,Leah and Audrey are AWESOME!!!!!!!
1,1260667748.301254,1260667774.479178,have you ever talked about talking?
1,1260667795.355510,1260667808.589576,ever seen a question mark?
1,1260667821.710898,1260667841.629871,now you have mwahahahha
1,1260667945.517477,1260667964.794623,cooelio means college math cirrculum
1,1260729073.35129,1260729102.958897,I got a feeling
3,1260762711.7942,1260824929.599358,So here's the new way.
0,1260824959.64662,1260825053.555341,I updated Return.
7,1260825131.733340,1260825177.151548,The text is taken from me.
666,1260924739.473939,1261056490.868304,I would graft gills to your lung.
101,1265461502.755341,1270104782.745864,this project does not get much attention
8,1289349313.22169,1304797973.229450,Frankly, my dear, I don't give a +(=$
1,1314194522.812251,1320952033.448251,love all the neighbors!
"""

import datetime

def past():
    i = 0
    for line in reversed(PAST.splitlines()):
        votes, ts_created, ts_posted, query = line.split(',', 3)
        age = to_age(datetime.datetime.fromtimestamp(float(ts_posted), tz=utc))
        if i == 0:
            if age.startswith("1 "):
                age = age.split()[1]
        yield (votes, age, query)
        i += 1
