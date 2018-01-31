import sys
import json
import logging
import textwrap
import unicurses
from . import Nexus, Artifactory, Validate, DataTree, Format

# The main class for the migration tool. Initializes unicurses, keeps track of
# windows and text attributes, and is in charge of redrawing the window when it
# gets resized.
class Screen(object):
    # Initialize unicurses. The window is a fixed 24 by 80 characters, which is
    # the standard VT100 screen size. If the available screen dimensions exceed
    # this, the window is framed. The main menu is then displayed. This
    # constructor takes a parameter 'screen', which is the window representing
    # the entire available screen.
    def __init__(self, screen, args):
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing screen.")
        self.args = args
        self.interactive = not args.non_interactive
        if self.interactive:
            res, ret = unicurses.KEY_RESIZE, unicurses.KEY_ENTER
            self.ctrlchars = (res, ret, ord('\n'), ord('\x1b'))
            self.msg = None
            self.screen = screen
            self.h, self.w = 22, 78
            self.wrap = textwrap.TextWrapper(width=self.w - 1)
            self.initattrs()
            self.frame = unicurses.newwin(self.h + 2, self.w + 2, 0, 0)
            unicurses.wborder(self.frame)
            self.win = unicurses.newwin(self.h, self.w, 0, 0)
            unicurses.keypad(self.win, 1)
        self.sslnoverify = sys.version_info >= (2, 7, 9) and args.ssl_no_verify
        self.loadst, self.savest = True, True
        self.state = DataTree(self, {})
        self.oldstate = DataTree(self, {})
        self.validate = Validate(self)
        self.format = Format(self)
        self.nexus = Nexus(self)
        self.artifactory = Artifactory(self)
        self.initstate(args.load_file)
        self.log.debug("Screen initialized.")

    def modified(self):
        self.state.prune()
        self.oldstate.prune()
        return self.state != self.oldstate

    def initstate(self, path):
        if path == None: return
        self.log.info("Loading configuration from file %s.", path)
        f, stat = None, None
        try:
            f = open(path, 'r')
            data = json.load(f)
            self.format.trim(data)
            self.state = DataTree(self, data)
            self.format.codePasswords(self.state, False)
            self.artifactory.checkArtifactory()
            self.nexus.checkNexus()
            self.validate()
            if self.state.valid == True:
                self.log.info("Configuration loaded successfully.")
            else:
                self.log.warning("Configuration loaded, errors found.")
            self.oldstate = self.state.clone()
            stat = True
        except:
            self.log.exception("Error loading configuration:")
            stat = "Unable to load from specified file."
        finally:
            if f != None: f.close()
        loadopt = self.state["Load Config JSON File"]
        saveopt = self.state["Save Config JSON File"]
        loadopt.data = path
        self.loadst = stat
        if stat == True: saveopt.data = path
        elif self.interactive: self.msg = ('err', stat)

    # Initialize the text attributes which will be used by this tool. Most of
    # these will be bold and some color.
    def initattrs(self):
        unicurses.init_pair(1, unicurses.COLOR_YELLOW, unicurses.COLOR_BLACK)
        unicurses.init_pair(2, unicurses.COLOR_GREEN, unicurses.COLOR_BLACK)
        unicurses.init_pair(3, unicurses.COLOR_CYAN, unicurses.COLOR_BLACK)
        unicurses.init_pair(4, unicurses.COLOR_RED, unicurses.COLOR_BLACK)
        unicurses.init_pair(5, unicurses.COLOR_WHITE, unicurses.COLOR_CYAN)
        unicurses.init_pair(6, unicurses.COLOR_WHITE, unicurses.COLOR_BLUE)
        self.attr = {}
        self.attr['ttl'] = unicurses.A_BOLD
        self.attr['key'] = unicurses.A_BOLD | unicurses.color_pair(1)
        self.attr['val'] = unicurses.A_BOLD | unicurses.color_pair(2)
        self.attr['slp'] = unicurses.A_BOLD | unicurses.color_pair(3)
        self.attr['err'] = unicurses.A_BOLD | unicurses.color_pair(4)
        self.attr['pfg'] = unicurses.A_BOLD | unicurses.color_pair(5)
        self.attr['pbg'] = unicurses.A_BOLD | unicurses.color_pair(6)

    def showchar(self, ch):
        encch = None
        try: encch = chr(ch).encode('string_escape')
        except ValueError:
            if ch == unicurses.KEY_ENTER: encch = '\\n'
            elif ch == unicurses.KEY_HOME: encch = 'HOME'
            elif ch == unicurses.KEY_END: encch = 'END'
            elif ch == unicurses.KEY_LEFT: encch = 'LEFT'
            elif ch == unicurses.KEY_RIGHT: encch = 'RIGHT'
            elif ch == unicurses.KEY_UP: encch = 'UP'
            elif ch == unicurses.KEY_DOWN: encch = 'DOWN'
            elif ch == unicurses.KEY_PPAGE: encch = 'PAGEUP'
            elif ch == unicurses.KEY_NPAGE: encch = 'PAGEDOWN'
            elif ch == unicurses.KEY_IC: encch = 'INSERT'
            elif ch == unicurses.KEY_BACKSPACE: encch = '\\x08'
            elif ch == unicurses.KEY_DC: encch = '\\x7f'
            else: encch = 'KEY_' + hex(ch)
        if encch == '\\n': return 'ENTER'
        elif encch == '\\t': return 'TAB'
        elif encch == '\\x08': return 'BACKSPACE'
        elif encch == '\\x7f': return 'DELETE'
        elif encch == '\\x1b': return 'ESCAPE'
        elif encch == '\\\\': return '\\'
        elif encch == '\\\'': return '\''
        elif encch == '\\\"': return '\"'
        else: return encch

    # A wrapper for window.getch(). The parameter 'win' is the window to getch
    # from. See the render() function for details on the parameter 'etc'. The
    # parameter 'redact' should be true when input should not be written to the
    # log (eg when the user is typing a password). This function exists because
    # unicurses notifies the application of a screen resize by buffering a
    # character unicurses.KEY_RESIZE in the input stream. This wrapper filters
    # out these resize events, and handles them using the render() function.
    def getch(self, win, etc=None, redact=False):
        while True:
            ch = unicurses.wgetch(win)
            if redact and ch not in self.ctrlchars:
                self.log.debug("Key '*' pressed.")
            else: self.log.debug("Key '%s' pressed.", self.showchar(ch))
            if ch == unicurses.KEY_RESIZE:
                self.log.debug("Screen resize detected.")
                self.render(etc)
            else: return ch

    # Redraw the screen. This function is called during initialization and after
    # a screen resize. It clears the screen, centers the frame and window, and
    # redraws them. This function takes an optional parameter 'etc', which is
    # passed if a pad is currently active, and contains a refrence to the pad as
    # well as refresh information for it, relative to the window. This allows an
    # active pad to be correctly redrawn after a resize.
    def render(self, etc=None):
        self.log.debug("Rendering the window.")
        unicurses.redrawwin(self.screen)
        unicurses.noutrefresh(self.screen)
        (hw, ww) = unicurses.getmaxyx(self.screen)
        (yw, xw) = (max(0, (hw - self.h)/2), max(0, (ww - self.w)/2))
        if yw > 0 and xw > 0:
            unicurses.mvwin(self.frame, yw - 1, xw - 1)
            unicurses.noutrefresh(self.frame)
        unicurses.mvwin(self.win, yw, xw)
        unicurses.noutrefresh(self.win)
        if etc != None:
            (buf, a, b, c, d, e, f) = etc
            (yb, xb) = unicurses.getbegyx(self.win)
            unicurses.prefresh(buf, a, b, c + yb, d + xb, e + yb, f + xb)
        unicurses.doupdate()
        self.log.debug("Window rendering complete.")
