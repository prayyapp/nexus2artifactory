import time
import unicurses

class Progress(object):
    def __init__(self, scr):
        self.scr = scr
        self.current = None
        self.currentartifact = None
        self.currentstep = 0
        if self.scr.interactive:
            self.title = "Running Migration ... "
            self.title = ' '*(self.scr.w - len(self.title)) + self.title
        self.started = None
        self.stepsmap = {}
        self.steps = []
        self.steps.append(["Repositories", 0, 0, 0, None])
        self.steps.append(["Groups", 0, 0, 0, None])
        self.steps.append(["Users", 0, 0, 0, None])
        self.steps.append(["Permissions", 0, 0, 0, None])
        self.steps.append(["LDAP Configs", 0, 0, 0, None])
        self.steps.append(["Artifacts", False, None, 0, 0])
        self.steps.append(["Finalizing", 0, 0, 0, None])
        for step in self.steps: self.stepsmap[step[0]] = step

    def show(self, conf):
        self.started = time.time()
        if self.scr.interactive:
            self.render()
            unicurses.wrefresh(self.scr.win)
        result = self.scr.artifactory.migrate(self, conf)
        if result == True:
            for step in self.steps:
                if step[3] > 0:
                    result = 'key', "Migration successful, but errors occurred."
                    break
            else: result = 'val', "Migration successful!"
        else: result = 'err', "Migration error: " + result
        if self.scr.interactive:
            self.render(result)
        return result

    def nextstep(self):
        self.current = None
        self.currentartifact = None
        self.currentstep += 1
        self.refresh()

    def refresh(self):
        if not self.scr.interactive: return
        self.render()
        unicurses.wrefresh(self.scr.win)

    def logsession(self, msg):
        log = []
        log.append("\nMigration Summary:\n\n")
        for stepn, step in enumerate(self.steps):
            name, done, total, errors, artifacts = step
            stat = None
            if errors > 0: stat = " ! "
            elif stepn < self.currentstep: stat = " + "
            elif stepn > self.currentstep: stat = "   "
            else: stat = " ~ "
            log.append(stat)
            stats = []
            stat = name + ' '*(15 - len(name))
            if total != None: stats.append(str(done) + '/' + str(total))
            if artifacts != None: stats.append(str(artifacts) + " Total")
            stat += ", ".join(stats)
            if errors > 0 and len(stats) > 0: stat += ", "
            log.append(stat)
            if errors > 0: log.append(str(errors) + " Errors")
            log.append("\n")
        timerep = self.drawTime(int(round(time.time() - self.started)))
        log.append("\n " + msg + "\n Completed in " + timerep + "\n")
        self.scr.log.info(''.join(log))

    def render(self, result=None):
        unicurses.wclear(self.scr.win)
        unicurses.waddstr(self.scr.win, self.title, self.scr.attr['ttl'])
        tdone, ttotal, terror, = 0, 0, 0
        mdone, mtotal, mname, mset = 0, 0, None, False
        for stepn, step in enumerate(self.steps):
            n, d, t, e, a = step
            if t == None:
                t = 1
                d = 1 if d else 0
            tdone += d
            ttotal += t
            terror += e
            if mdone >= mtotal and d > 0 and not mset:
                mdone, mtotal, mname = d, t, n
            else: mset = True
            self.renderStep(stepn, step)
        unicurses.waddstr(self.scr.win, "\n Total Progress:\n")
        self.renderProgress(tdone, ttotal)
        if result != None:
            status, msg = result
            timerep = self.drawTime(int(round(time.time() - self.started)))
            msg = "\n " + msg
            unicurses.waddstr(self.scr.win, msg, self.scr.attr[status])
            msg = "\n Completed in " + timerep
            msg += "\n\n Press 'q' to continue.\n\n"
            unicurses.waddstr(self.scr.win, msg)
            unicurses.flushinp()
            while chr(self.scr.getch(self.scr.win)) != 'q': pass
        elif mname != None:
            unicurses.waddstr(self.scr.win, "\n " + mname + " Progress:\n")
            self.renderProgress(mdone, mtotal)
            if self.current != None:
                unicurses.waddstr(self.scr.win, self.current + "\n")
            if self.currentartifact != None:
                unicurses.waddstr(self.scr.win, self.currentartifact + "\n")
            unicurses.waddstr(self.scr.win, "\n")
        else: unicurses.waddstr(self.scr.win, "\n")

    def renderStep(self, stepn, step):
        name, done, total, errors, artifacts = step
        stat, color = None, None
        if errors > 0: stat, color = " ! ", 'err'
        elif stepn < self.currentstep: stat, color = " + ", 'val'
        elif stepn > self.currentstep: stat, color = "   ", 'val'
        else: stat, color = " ~ ", 'slp'
        unicurses.waddstr(self.scr.win, stat, self.scr.attr[color])
        stats = []
        stat = name + ' '*(15 - len(name))
        if total != None: stats.append(str(done) + '/' + str(total))
        if artifacts != None: stats.append(str(artifacts) + " Total")
        stat += ", ".join(stats)
        if errors > 0 and len(stats) > 0: stat += ", "
        unicurses.waddstr(self.scr.win, stat)
        if errors > 0:
            stat = str(errors) + " Errors"
            unicurses.waddstr(self.scr.win, stat, self.scr.attr['err'])
        unicurses.waddstr(self.scr.win, "\n")

    def renderProgress(self, done, total):
        perc = '0%'
        if total != 0:
            perc = str(int(round(float(100*done)/float(total)))) + '%'
        rpad = self.scr.w/2 - 3
        lpad = self.scr.w - len(perc) - rpad - 2
        bar = ' '*lpad + perc + ' '*rpad
        fill = 0
        if total != 0:
            fill = int(round(float((self.scr.w - 2)*done)/float(total)))
        unicurses.waddstr(self.scr.win, " ")
        unicurses.waddstr(self.scr.win, bar[:fill], self.scr.attr['pfg'])
        unicurses.waddstr(self.scr.win, bar[fill:], self.scr.attr['pbg'])
        unicurses.waddstr(self.scr.win, "\n")

    def drawTime(self, allsecs):
        secs, allmins = allsecs%60, allsecs//60
        mins, allhours = allmins%60, allmins//60
        hours, days = allhours%24, allhours//24
        timerep, include = [], False
        if include or days > 0:
            include = True
            timerep.append(str(days) + 'd')
        if include or hours > 0:
            include = True
            timerep.append(str(hours) + 'h')
        if include or mins > 0:
            timerep.append(str(mins) + 'm')
        timerep.append(str(secs) + 's')
        return ' '.join(timerep)
