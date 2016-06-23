#!/usr/bin/env python2
import os
import ssl
import unicurses
from functools import wraps
from nex2art.menu import Safety, Main
from nex2art.core import Screen

# Some versions of SSL have a bug that causes an exception to be thrown when
# a connection is made using TLSv1.1/TLSv1.2. This hack works around this
# problem by forcing TLSv1.0.
def fixssl():
    def sslwrap(func):
        @wraps(func)
        def bar(*args, **kw):
            kw['ssl_version'] = ssl.PROTOCOL_TLSv1
            return func(*args, **kw)
        return bar
    ssl.wrap_socket = sslwrap(ssl.wrap_socket)

# Start the tool by initializing unicurses and creating a new Screen object.
# Before doing so, set the ESCDELAY environment variable to 25, in an attempt to
# mitigate the delay following the pressing of the escape key during line
# editing.
if __name__ == '__main__':
    os.environ.setdefault('ESCDELAY', '25')
    fixssl()
    try:
        stdscr = unicurses.initscr()
        unicurses.noecho()
        unicurses.cbreak()
        try: unicurses.start_color()
        except: pass
        scr = Screen(stdscr)
        saf = Safety(scr)
        win = Main(scr)
        scr.render()
        while True:
            win.show()
            if not scr.modified() or saf.show(): break
    finally:
        if 'stdscr' in locals():
            unicurses.echo()
            unicurses.nocbreak()
            unicurses.endwin()
