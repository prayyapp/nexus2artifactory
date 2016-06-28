#!/usr/bin/env python2
import os
import logging
import unicurses
from nex2art.menu import Safety, Main
from nex2art.core import Setup, Screen

# Start the tool by initializing unicurses and creating a new Screen object.
# Before doing so, set the ESCDELAY environment variable to 25, in an attempt to
# mitigate the delay following the pressing of the escape key during line
# editing.
if __name__ == '__main__':
    setup = Setup()
    logging.info("Initializing Nexus migration tool.")
    os.environ.setdefault('ESCDELAY', '25')
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
    except:
        logging.exception("Error running Nexus migration tool:")
        raise
    finally:
        logging.info("Terminating Nexus migration tool.")
        logging.shutdown()
        if 'stdscr' in locals():
            unicurses.echo()
            unicurses.nocbreak()
            unicurses.endwin()
