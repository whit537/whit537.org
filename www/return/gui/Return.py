"""GUI automation to populate Google query from whit537.org/return/next.txt.
"""
import sys
import time
import urllib

import SendKeys


def handle_query(query):
    SendKeys.SendKeys("^a")        # Select All
    SendKeys.SendKeys("{DELETE}")  # Delete
    for c in query:
        if c in "+^%~{}[]()":
            # escape per http://www.rutherfurd.net/python/sendkeys/
            c = "{%s}" % c
        SendKeys.SendKeys(c, with_spaces=True)
        time.sleep(0.05)


def loop(url, nsec):
    SendKeys.SendKeys("%{TAB}")
    while 1:
        time.sleep(nsec)
        try:
            fp = urllib.urlopen(url)
        except IOError, exc:
            print exc
            continue
        next = fp.read()
        if next:
            timestamp, query = next.split(",", 1)
            if query:   # put the query in the search box
                handle_query(query)
            else:       # competition is over, sleep while voting
                wait_for_voting = int(timestamp) - time.time() - nsec + 1
                if wait_for_voting > 0:
                    time.sleep(wait_for_voting)


if __name__ == "__main__":
    if "--dev" in sys.argv:
        base = "http://www.whit537.org.dev"
        sys.argv.remove("--dev")
    else:
        base = "http://www.whit537.org"
    url = base + "/return/next.txt"
    nsec = int(sys.argv[1])
    loop(url, nsec)
