#!/usr/bin/env python2
import os
import sys
import logging
import unicurses
from nex2art.menu import Safety, Main
from nex2art.core import Setup, Screen, Progress

# Start the tool by initializing unicurses and creating a new Screen object.
# Before doing so, set the ESCDELAY environment variable to 25, in an attempt to
# mitigate the delay following the pressing of the escape key during line
# editing.
def initInteractive(setup):
    logging.info("Initializing Nexus migration tool.")
    os.environ.setdefault('ESCDELAY', '25')
    try:
        stdscr = unicurses.initscr()
        unicurses.noecho()
        unicurses.cbreak()
        try: unicurses.start_color()
        except: pass
        scr = Screen(stdscr, setup.args)
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

def initNonInteractive(setup):
    logging.info("Initializing Nexus migration tool.")
    status, prog = None, None
    try:
        scr = Screen(None, setup.args)
        prog = Progress(scr)
        logging.info("Attempting to run migration.")
        if scr.loadst != True:
            logging.warning("Unable to run migration: %s", str(scr.loadst))
            sys.exit(1)
        if scr.state.valid != True:
            logging.warning("Unable to run migration, errors found.")
            sys.exit(1)
        status = prog.show(scr.state.todict())
        if status == True: logging.info("Migration successfully run.")
        else:
            logging.warning("Error running migration: %s.", status)
            sys.exit(1)
    except BaseException as ex:
        if not isinstance(ex, SystemExit):
            logging.exception("Error running Nexus migration tool:")
        raise
    finally:
        if status != None and prog != None: prog.logsession()
        logging.info("Terminating Nexus migration tool.")
        logging.shutdown()

if __name__ == '__main__':
    setup = Setup()
    if setup.args.non_interactive: initNonInteractive(setup)
    else: initInteractive(setup)
