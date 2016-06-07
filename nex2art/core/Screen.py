import textwrap
import unicurses
from . import Nexus, Artifactory

# The main class for the migration tool. Initializes unicurses, keeps track of
# windows and text attributes, and is in charge of redrawing the window when it
# gets resized.
class Screen:
    # Initialize unicurses. The window is a fixed 24 by 80 characters, which is
    # the standard VT100 screen size. If the available screen dimensions exceed
    # this, the window is framed. The main menu is then displayed. This
    # constructor takes a parameter 'screen', which is the window representing
    # the entire available screen.
    def __init__(self, screen):
        self.msg = None
        self.screen = screen
        self.mainmenu = None
        self.oldstate = None
        self.h, self.w = 22, 78
        self.nexus = Nexus()
        self.artifactory = Artifactory(self)
        self.wrap = textwrap.TextWrapper(width=self.w)
        self.initattrs()
        self.frame = unicurses.newwin(self.h + 2, self.w + 2, 0, 0)
        unicurses.wborder(self.frame)
        self.win = unicurses.newwin(self.h, self.w, 0, 0)
        unicurses.keypad(self.win, 1)

    def modified(self):
        return self.mainmenu.collectconf() != self.oldstate

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

    # A wrapper for window.getch(). The parameter 'win' is the window to getch
    # from. See the render() function for details on the parameter 'etc'. This
    # function exists because unicurses notifies the application of a screen
    # resize by buffering a character unicurses.KEY_RESIZE in the input stream.
    # This wrapper filters out these resize events, and handles them using the
    # render() function.
    def getch(self, win, etc=None):
        while True:
            ch = unicurses.wgetch(win)
            if ch == unicurses.KEY_RESIZE:
                self.render(etc)
            else: return ch

    # Redraw the screen. This function is called during initialization and after
    # a screen resize. It clears the screen, centers the frame and window, and
    # redraws them. This function takes an optional parameter 'etc', which is
    # passed if a pad is currently active, and contains a refrence to the pad as
    # well as refresh information for it, relative to the window. This allows an
    # active pad to be correctly redrawn after a resize.
    def render(self, etc=None):
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
