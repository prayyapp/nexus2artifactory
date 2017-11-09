import unicurses
from . import hlp
from . import Option

# The base menu class. A menu consists of a list of options, each of which can
# be accessed by pressing an associated key on the keyboard. Each option may
# have an associated value, which may be editable by some means. When an
# option's key is pressed, it may have a variety of effects, such as editing a
# value, producing arbitrary side effects, opening the contextual help system,
# exiting the menu, or opening a child menu.
class Menu(object):
    # Initialize the menu. The parameter 'scr' is the Screen object to use, to
    # access shared resources such as the unicurses windows and text attributes.
    # The parameter 'title' is the title of the menu, which is displayed in the
    # top right corner of the window.
    def __init__(self, scr, path, title, defeditor=None):
        self.option = None
        self.defeditor = defeditor
        self.scr = scr
        self.path = path
        self.pagedopts = []
        self.filtpagedopts = []
        self.title = title
        self.navopts = []
        self.motnopts = [
            None,
            self.mkopt('<-/->', "Previous Page / Next Page", None)]
        filt = ['|', self.setfilter]
        self.filtopt = self.mkopt('f', "Search Filter", filt, save=False)
        self.page = 1
        self.filter = []

    # Create an option. This is a simple convenience function which places its
    # arguments into a dictionary, and returns the dictionary. The parameters
    # are such:
    # - 'key': single-character string representing the key on the keyboard
    #   which must be typed in order to access this option
    # - 'text': text displayed in the menu to represent this option
    # - 'act': action or list of actions that should be taken when this option
    #   is accessed
    # - 'val': initial value this option should be set to
    # - 'alt': action or list of actions that should be taken when this option
    #   is accessed via an alternative action keypress
    # - 'hdoc': documentation string to print when this option is selected by
    #   the contextual help system (or the value False if this option should
    #   instead exit the contextual help system)
    def mkopt(self, key, text, act,
              val=None, alt=None, save=None, hdoc=None, path=None):
        if hdoc == None and text in hlp: hdoc = hlp[text]
        if isinstance(hdoc, basestring):
            hdoc = self.scr.wrap.fill(' '.join(hdoc.split()))
        if not isinstance(act, list): act = [act]
        if not isinstance(alt, list): alt = [alt]
        mypath, realpath, shouldsave, control = None, None, True, False
        if path != None: mypath = path
        if self.path != None:
            realpath = self.path[:]
            realpath.append(text)
            if mypath == None: mypath = realpath
        if key in ('<-/->', 'INFO') or mypath == None: shouldsave = False
        if key == '<-/->' or mypath == None: control = True
        if None in act:
            shouldsave = False
            if key != 'INFO': control = True
        menus = []
        for axt in act, alt:
            for n, x in enumerate(axt):
                if isinstance(x, dict) and 'class' in x:
                    axt[n] = x['class'](self.scr, realpath, *x['args'], **x['kwargs'])
                y = axt[n]
                if isinstance(y, Menu):
                    shouldsave = False
                    menus.append(y)
                if y in ('?', '&'): shouldsave, control = False, True
        if save == True: control = False
        if save == None: save = shouldsave
        vals = {'key': key, 'val': val, 'text': text, 'act': act, 'help': hdoc,
                'alt': alt, 'stat': True, 'save': save, 'wait': False}
        if hasattr(self, 'leaf') and self.leaf == True: control = True
        if control: vals['save'], opt = False, vals
        else: opt = Option(self.scr, vals, mypath, realpath, len(menus) > 0)
        for menu in menus: menu.option = opt
        return opt

    def submenu(self, cls, *args, **kwargs):
        return {'class': cls, 'args': args, 'kwargs': kwargs}

    # This function allows values that are longer than 80 characters to be
    # displayed next to an option. If printing a value would print past the end
    # of the line, the middle section of the value is cut out and replaced with
    # the string '...' before printing. This makes the first and last parts
    # (usually the most important parts) visible in the window, without taking
    # up too much space. The parameter 'string' is the string to print, and the
    # parameter 'attr' is the name of the text attribute to use when printing.
    # The parameter 'rpad' is the number of character widths that should be left
    # at the end of the line once the string is printed.
    def dotstr(self, string, attr, rpad=0):
        if attr == None: attr = unicurses.A_NORMAL
        offs = unicurses.getyx(self.scr.win)[1]
        if len(string) > self.scr.w - offs - rpad:
            lstr = string[:(self.scr.w - offs - rpad)/2 - 1]
            rstr = string[-(self.scr.w - offs - rpad - len(lstr) - 3):]
            unicurses.waddstr(self.scr.win, lstr, attr)
            unicurses.waddstr(self.scr.win, "...")
            unicurses.waddstr(self.scr.win, rstr, attr)
        else: unicurses.waddstr(self.scr.win, string, attr)

    # Render the menu to the window. Clear the window, and if there's a message
    # to display, print it across the bottom. Print the title in the top right
    # corner, and then print all the options. For each option, print the key to
    # press to select the option, the associated text, and the status and value
    # if applicable. If an option is None, print a spacer instead.
    def render(self):
        unicurses.wclear(self.scr.win)
        if self.scr.msg != None:
            unicurses.wmove(self.scr.win, self.scr.h - 1, 0)
            if isinstance(self.scr.msg, basestring):
                unicurses.waddnstr(self.scr.win, self.scr.msg, self.scr.w)
            elif isinstance(self.scr.msg, tuple):
                attr = self.scr.attr[self.scr.msg[0]]
                msg = self.scr.msg[1]
                unicurses.waddnstr(self.scr.win, msg, self.scr.w, attr)
            unicurses.wmove(self.scr.win, 0, 0)
        unicurses.waddstr(self.scr.win, self.titlebar, self.scr.attr['ttl'])
        for opt in self.curropts:
            if opt == None:
                unicurses.waddstr(self.scr.win, "\n")
                continue
            key = opt['key'] + ": "
            unicurses.waddstr(self.scr.win, key, self.scr.attr['key'])
            if not isinstance(opt['val'], basestring):
                pad = 2 if opt['stat'] != True else 0
                if opt['wait'] == True or opt['val'] == True: pad += 2
                self.dotstr(opt['text'], None, pad)
            else: unicurses.waddstr(self.scr.win, opt['text'])
            attr = self.scr.attr['val']
            if opt['stat'] != True:
                attr = self.scr.attr['err']
                unicurses.waddstr(self.scr.win, " !", attr)
            if opt['wait'] == True:
                unicurses.waddstr(self.scr.win, " ~", self.scr.attr['slp'])
            elif opt['val'] == True:
                unicurses.waddstr(self.scr.win, " +", attr)
            elif opt['val'] == (None,):
                unicurses.waddstr(self.scr.win, " unchanged", self.scr.attr['slp'])
            elif isinstance(opt['val'], (basestring, list)):
                if len(opt['text']) > 0: unicurses.waddstr(self.scr.win, " ")
                value = opt['val']
                if isinstance(value, list): value = ','.join(value)
                if '*' in opt['act']: value = '*'*len(value)
                self.dotstr(value, attr)
            if unicurses.getyx(self.scr.win)[1] > 0:
                unicurses.waddstr(self.scr.win, "\n")
        unicurses.waddstr(self.scr.win, "\n")

    # Display the menu. Render it, then wait for a keypress that matches one of
    # the options, and then execute the associated actions. All of this runs in
    # a loop, which ensures that the menu continues to accept input until it is
    # closed.
    def show(self):
        if hasattr(self, 'initialize'): self.initialize()
        if self.filtopt != None: self.setfilter(self.filtopt)
        while True:
            sel = None
            self.pagebuild()
            self.render()
            while True:
                key = self.scr.getch(self.scr.win)
                try:
                    if key in self.keymap:
                        sel = self.keymap[key]
                        break
                    if chr(key) in self.keymap:
                        sel = self.keymap[chr(key)]
                        break
                except ValueError: pass
            self.scr.msg = None
            self.render()
            if self.runact(sel, sel['act']): return

    # Given an option 'sel' and a list of actions 'acts', execute the actions
    # list. The actions list is executed one at a time, in order. Each action in
    # the list can be any of the following:
    # - an arbitrary function to run, which takes the option as an argument
    # - a Menu object: displayed as a child menu
    # - None: exits the current menu
    # - '?': starts the contextual help system
    # - '&': queries for another keypress, and runs that key's alt action
    # - '+': inverts the option's value as a boolean
    # - '|': displays a line editor, allowing the user to modify the option's
    #   value as a string
    # - '*': displays a silent line editor, allowing a sensitive value (such as
    #   a password) to be entered by the user
    # When all actions have been executed, the value is validated, and the
    # status is set accordingly.
    def runact(self, sel, acts):
        cont = True
        for act in acts:
            if act == None:
                self.page = 1
                return True
            elif hasattr(act, 'show'): act.show()
            elif hasattr(act, '__call__'): cont = self.showCall(sel, act)
            elif act == '?': self.showHelp()
            elif act == '&': self.showAlt()
            elif act == '+': sel['val'] = not sel['val']
            elif act == '|': cont = self.showLineEdit(sel, False)
            elif act == '*': cont = self.showLineEdit(sel, True)
            if cont == False: break
            elif sel['wait'] == True: sel['wait'] = False
        if hasattr(sel, 'path'): self.scr.validate(sel.path)
        valid = sel['stat']
        if isinstance(valid, basestring): self.scr.msg = ('err', valid)

    # Run the action, which is an arbitrary function. While the action is
    # running, display a tilde next to the option to show that it's busy. The
    # parameter 'sel' is the selected option, and 'act' is the action in
    # question.
    def showCall(self, sel, act):
        sel['wait'] = True
        self.render()
        unicurses.wrefresh(self.scr.win)
        cont = act(sel)
        sel['wait'] = False
        self.render()
        unicurses.flushinp()
        return cont != False

    # Query for a key which matches an option, and run that option's alternate
    # action.
    def showAlt(self):
        unicurses.waddstr(self.scr.win, "Type a command key: ")
        while True:
            key = chr(self.scr.getch(self.scr.win))
            if key in self.keymap and False not in self.keymap[key]['alt']:
                self.runact(self.keymap[key], self.keymap[key]['alt'])
                break

    # Query for a key which matches an option, and display contextual help for
    # that option.
    def showHelp(self):
        string = "Type a command key for contextual help: "
        unicurses.waddstr(self.scr.win, string)
        while True:
            try:
                key = chr(self.scr.getch(self.scr.win))
            except ValueError: continue
            if key in self.keymap and self.keymap[key]['help'] != None:
                if self.keymap[key]['help'] == False: break
                unicurses.wclear(self.scr.win)
                err = self.keymap[key]['stat']
                if isinstance(err, basestring):
                    attr = self.scr.attr['err']
                    unicurses.wmove(self.scr.win, self.scr.h - 1, 0)
                    unicurses.waddnstr(self.scr.win, err, self.scr.w, attr)
                    unicurses.wmove(self.scr.win, 0, 0)
                title = self.keymap[key]['text']
                title = ' '*(self.scr.w - len(title) - 6) + title + " Help \n"
                unicurses.waddstr(self.scr.win, title, self.scr.attr['ttl'])
                unicurses.waddstr(self.scr.win, self.keymap[key]['help'])
                string = "\n\nPress 'q' to exit help.\n\n"
                unicurses.waddstr(self.scr.win, string)
                while chr(self.scr.getch(self.scr.win)) != 'q': pass
                break

    # Display an option's value in a simple line editor, and allow the user to
    # edit the value as a string. The editor window 'follows' the cursor, so
    # that the current location is always in view, even if the string is much
    # longer than the available space on the screen. A handful of special keys
    # are supported, such as Home and End to move the cursor respectively to the
    # beginning and end of the string, Left and Right to move the cursor
    # respectively left and right by one character, and Backspace and Delete to
    # delete respectively the previous and next character in the string. Return
    # or Enter will exit the editor and save the new value, and Escape will exit
    # the editor and discard the new value. The parameter 'sel' is the selected
    # option, and 'quiet' is a boolean value describing whether to hide the text
    # being edited (pass True if, say, the field contains a password).
    def showLineEdit(self, sel, quiet):
        maxwidth = 4096
        fw, hw = self.scr.w - 2, (self.scr.w - 2)/2
        unicurses.waddstr(self.scr.win, "Edit " + sel['text'] + ":\n> ")
        unicurses.noutrefresh(self.scr.win)
        (yn, xn) = unicurses.getyx(self.scr.win)
        buf = unicurses.newpad(1, maxwidth + 1)
        unicurses.keypad(buf, 1)
        offs, length, submit = 0, 0, False
        if not quiet and sel['val'] != None and sel['val'] != (None,):
            length = len(sel['val'])
            unicurses.waddstr(buf, sel['val'])
            offs = max(0, length/hw - 1)
            (yb, xb) = unicurses.getbegyx(self.scr.win)
            (yp, xp) = (yn + yb, xn + xb)
            unicurses.prefresh(buf, 0, offs*hw, yp, xp, yp, xp + fw - 1)
        unicurses.doupdate()
        while True:
            if quiet: ch = self.scr.getch(buf, redact=True)
            else:
                etc = (buf, 0, offs*hw, yn, xn, yn, xn + fw - 1)
                ch = self.scr.getch(buf, etc)
            (y, x) = unicurses.getyx(buf)
            if ch in (ord('\n'), unicurses.KEY_ENTER):
                sel['val'] = unicurses.mvwinstr(buf, 0, 0, length)
                if sel['val'] != None and len(sel['val']) == 0:
                    sel['val'] = None
                submit = True
                break
            elif ch == ord('\x1b'): break
            elif ch == unicurses.KEY_HOME and x > 0:
                unicurses.wmove(buf, y, 0)
            elif ch == unicurses.KEY_END and x < length:
                unicurses.wmove(buf, y, length)
            elif ch == unicurses.KEY_LEFT and x > 0:
                unicurses.wmove(buf, y, x - 1)
            elif ch == unicurses.KEY_RIGHT and x < length:
                unicurses.wmove(buf, y, x + 1)
            elif ch in (ord('\b'), ord('\x7f'), unicurses.KEY_BACKSPACE,
                        unicurses.KEY_DC) and x > 0:
                unicurses.wmove(buf, y, x - 1)
                unicurses.wdelch(buf)
                length -= 1
            elif ord(' ') <= ch <= ord('~') and length < maxwidth:
                unicurses.winsstr(buf, chr(ch))
                length += 1
                unicurses.wmove(buf, y, x + 1)
            else: continue
            if quiet: continue
            oldoffs, offs = offs, max(0, unicurses.getyx(buf)[1]/hw - 1)
            if oldoffs < offs and maxwidth - offs*hw < fw:
                unicurses.wclrtoeol(self.scr.win)
                unicurses.noutrefresh(self.scr.win)
            (yb, xb) = unicurses.getbegyx(self.scr.win)
            (yp, xp) = (yn + yb, xn + xb)
            unicurses.prefresh(buf, 0, offs*hw, yp, xp, yp, xp + fw - 1)
            unicurses.doupdate()
        return submit

    # Build the page for display by Menu's rendering functions, in case
    # pagination is required. Calculate the number of options per page, as well
    # as the total number of pages, and ensure that the current page is within
    # that range. Set the title using this information. Extract the subset of
    # options from the 'pagedopts' list, and append the 'opts' list. Finally,
    # build a new keymap for this updated options list.
    def pagebuild(self):
        index = 1
        if (self.defeditor == None or len(self.pagedopts) <= 0 or
                (len(self.pagedopts) == 1 and
                     self.pagedopts[0]['key'] == 'INFO')):
            self.navopts = []
        elif (len(self.filtpagedopts) <= 0 or
                  (len(self.filtpagedopts) == 1 and
                       self.filtpagedopts[0]['key'] == 'INFO')):
            self.navopts = [None, self.filtopt]
        else:
            medit = self.mkopt('m', "Mass Edit", self.massedit, save=False)
            self.navopts = [None, self.filtopt, medit]
        totallen = len(self.filtpagedopts) + len(self.opts)
        optslen = self.scr.h - len(self.navopts) - 4
        if len(self.filtpagedopts) <= 10 and totallen <= optslen:
            for opt in self.filtpagedopts:
                if opt['key'] == None or len(opt['key']) <= 1:
                    opt['key'] = str(0 if index == 10 else index)
                    index += 1
            self.curropts = self.filtpagedopts + self.navopts + self.opts
            padding = self.scr.w - len(self.title) - 1
            self.titlebar = ' '*padding + self.title + ' '
            self.buildKeymap()
            return
        maxset = self.scr.h - len(self.opts) - len(self.motnopts) - 4
        maxset -= len(self.navopts)
        maxset = min(10, maxset)
        pagect = len(self.filtpagedopts)/maxset
        if len(self.filtpagedopts)%maxset > 0: pagect += 1
        if self.page < 1: self.page = 1
        if self.page > pagect: self.page = pagect
        title = self.title + " (Page " + str(self.page)
        title += " of " + str(pagect) + ")"
        self.titlebar = ' '*(self.scr.w - len(title) - 1) + title + ' '
        beg = (self.page - 1)*maxset
        end = self.page*maxset
        for opt in self.filtpagedopts[beg:end]:
            if opt['key'] == None or len(opt['key']) <= 1:
                opt['key'] = str(0 if index == 10 else index)
                index += 1
        self.curropts = self.filtpagedopts[beg:end] + self.motnopts
        self.curropts += self.navopts + self.opts
        self.buildKeymap()

    def setfilter(self, newfilter):
        if newfilter['val'] == None:
            self.filter = []
            self.filtpagedopts = self.pagedopts
        else:
            def f(x): return x['alt'][0].filt(self.filter)
            self.filter = newfilter['val'].split()
            self.filtpagedopts = filter(f, self.pagedopts)
            if len(self.filtpagedopts) <= 0:
                msg = "no results found"
                self.filtpagedopts = [self.mkopt('INFO', msg, None)]

    def massedit(self, _):
        editor = self.defeditor(self.scr)
        editor.show()
        updates = {}
        for opt in editor.opts:
            if opt == None or opt['alt'][0] != editor.massreset: continue
            if opt['val'] == (None,): continue
            updates[opt['text']] = opt['val']
        if len(updates) <= 0: return
        for popt in self.filtpagedopts:
            for itemn, item in self.scr.state[popt['alt'][0].path].items():
                if itemn in updates: item.data = updates[itemn]

    def massreset(self, opt):
        opt['val'] = (None,)

    def massinit(self, _):
        for opt in self.opts:
            if opt == None or opt['alt'][0] != self.massreset: continue
            opt['val'] = (None,)

    # Decrement the current page, and rebuild. Meant to be called as an option's
    # action.
    def pageprev(self, _):
        self.page -= 1

    # Increment the current page, and rebuild. Meant to be called as an option's
    # action.
    def pagenext(self, _):
        self.page += 1

    # A lot of the time, options in the option list need to be accessed by their
    # 'key' property. It makes sense to have a dictionary for these times, even
    # though that wouldn't work for the option list in general because it
    # requires things like ordered elements and spacer elements. This function
    # should be run whenever the option list changes. It iterates through the
    # option list, and builds a dictionary of options based on their keys.
    def buildKeymap(self):
        self.keymap = {}
        for opt in self.curropts:
            if opt != None:
                self.keymap[opt['key']] = opt
                if opt['key'] == '<-/->':
                    opt1 = opt.copy()
                    opt2 = opt.copy()
                    opt1['act'] = [self.pageprev]
                    opt2['act'] = [self.pagenext]
                    self.keymap[unicurses.KEY_LEFT] = opt1
                    self.keymap[unicurses.KEY_RIGHT] = opt2
