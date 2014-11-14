import sys
import gflags

def set_gflags():
  try:
    argv = gflags.FLAGS(sys.argv) # parse flags
    # now argv holds the non-flag arguments
    # e.g. hey.py --what=2 777
    # now argv is [777], I bet
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)
