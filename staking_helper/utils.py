import sys
import time


def error(msg):
    print(msg)
    sys.exit(1)


def ts_now():
    return int(time.time() * 1000)
