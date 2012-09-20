#!/usr/bin/env python
import commands
import os
import re
import sys
import time
import traceback


# Helpers
# =======

DAT = "foo"
LOG = "bar"

def clear():
    for filename in (DAT, LOG):
        if os.path.isfile(filename):
            os.remove(filename)

def do(cmd):
    return commands.getoutput("./return %s %s %s" % (DAT, LOG, cmd))


def test(cmd, expected):
    actual = do(cmd)
    if '-v' in sys.argv:
        print actual
    else:
        if isinstance(expected, str):       # string
            expected = expected.rstrip("\n")
            failure = actual != expected
        else:                               # re
            failure = expected.match(actual) is None
            expected = expected.pattern
        if failure:
            linenos = []
            for frame in traceback.extract_stack():
                linenos.append(str(frame[1]))
            lineno = ",".join(linenos[:-1])
            print "\nfailed test on line %s\n" % lineno
            print "got:\n%s" % actual
            print "\nnot:\n%s" % expected
            print
            raise SystemExit
        sys.stdout.write("."); sys.stdout.flush()


# Tests
# =====

# File starts empty.
clear()
test("list", "")


# Foo.
test("A", "")
test("B", "")
test("B", "") # duplicates silently ignored during competition
test("C", "")
test("D", "")
test("E", "")
test("F", "")
test("G", "")
test("list", """\
1,0,A
2,0,B
3,0,C
4,0,D
5,0,E
6,0,F
7,0,G
""")


# Basics
# ======
clear()

# Add a query, it persists.
test('"Snoop Dogg"', "")
test("list", """\
1,0,Snoop Dogg
""")

# Add another query.
test('"Natty Dread"', "")
test("list", """\
1,0,Snoop Dogg
2,0,Natty Dread
""")

# Next doesn't return anything until the queue is full.
test("next", "")


# Matching
# ========
clear()

# Queries are matched case-insensitively.
test('"Snoop Dogg"', "")
test('"snoop DOGG"', "")
test("list", """\
1,0,Snoop Dogg
""")


# Test priority/next interaction. 
# ===============================
clear()

# Fill up the queue ... 
for i in range(10):
    test(str(i), "")
    time.sleep(0.5) # push g_voting_deadline out into the future a bit
test("list", """\
1,0,0
2,0,1
3,0,2
4,0,3
5,0,4
6,0,5
7,0,6
8,0,7
9,0,8
10,0,9
""")

# ... and upvote the last.
time.sleep(1) # ensure we are into voting
test("9", "")
test("list", """\
1,1,9
2,0,0
3,0,1
4,0,2
5,0,3
6,0,4
7,0,5
8,0,6
9,0,7
10,0,8
""")

# While we wait for the voting period to be over, returns deadline.
test("next", re.compile("\d{10},"))

# While we're waiting for g_voting_deadline, try overflowing the heap.
test("overflow", "Sorry, the queue is full. Time for voting!")

# Still waiting for voting. 
test("next", re.compile("\d{10},"))

# Wait for the end of voting ...
time.sleep(6) # (0.5 seconds * 10 items) + 1 for good measure

# Now pop the next query. This clears the queue!
test('next', re.compile("\d{10}\.\d+,9"))
test("list", "")

# Popping an empty queue returns none.
test("next", "")

# And now we can start adding again.
test("overflow", "")


# Test MAX_QUERY_LEN
# ==================
clear()
test("0123456789012345678901234567890123456789", "")
test( "01234567890123456789012345678901234567890"
    , "Sorry, we don't take more than 40 characters."
     )


# Be more sure about timing.
# ==========================
def test_timing(i):
    clear()
    
    # fill queue most of the way and then wait
    for i in range(9):
        test(str(i), "")
    time.sleep(i)
    
    # now finish filling it
    test("9", "")
    test("10", "Sorry, the queue is full. Time for voting!")
    test("list", """\
1,0,0
2,0,1
3,0,2
4,0,3
5,0,4
6,0,5
7,0,6
8,0,7
9,0,8
10,0,9""")
    
    # While we wait for the voting period to be over, next returns nothing
    test("next", re.compile("\d{10},"))
    time.sleep(i*0.8)
    test("next", re.compile("\d{10},"))
    time.sleep(i*0.4)
    test("next", re.compile("\d{10}\.\d+,0"))

test_timing(5)
if '-a' in sys.argv:
    test_timing(10)
    test_timing(100)


# List is sorted by both priority and creation time.
# ==================================================
# Before I used heapsort in list() I actually tried to keep the heap sorted at 
# all times, which of course kind of defeats the purpose of a heap. For this 
# reason I want to have multiple levels in this next test; that's where the 
# bugs in my keep-it-sorted attempt were showing up.
clear()

entries = ("foo", "bar", "baz", "buz", "blee", "bloo", "blah", "blam", "flam")
for entry in entries:
    test(entry, "")
time.sleep(1) # give ourselves some time to run voting tests
test("ham", "")

test("list", """\
1,0,foo
2,0,bar
3,0,baz
4,0,buz
5,0,blee
6,0,bloo
7,0,blah
8,0,blam
9,0,flam
10,0,ham
""")

# something entered late jumps out front when upvoted
test("blam", "")
test("list", """\
1,1,blam
2,0,foo
3,0,bar
4,0,baz
5,0,buz
6,0,blee
7,0,bloo
8,0,blah
9,0,flam
10,0,ham
""")


# but something entered earlier takes the lead when also upvoted
test("baz", "")
test("list", """\
1,1,baz
2,1,blam
3,0,foo
4,0,bar
5,0,buz
6,0,blee
7,0,bloo
8,0,blah
9,0,flam
10,0,ham
""")

# need to upvote again to trump earlier one
test("blam", "")
test("list", """\
1,2,blam
2,1,baz
3,0,foo
4,0,bar
5,0,buz
6,0,blee
7,0,bloo
8,0,blah
9,0,flam
10,0,ham
""")


print
clear()
