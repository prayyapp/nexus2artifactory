import xml.etree.ElementTree as ET
from ..core import Menu
from . import ChooseList

class RepoEdit(Menu):
    def __init__(self, scr, parent, repo):
        Menu.__init__(self, scr, "Edit Repository Options")
        self.parent = parent
        self.cls, self.typ = repo['class'], repo['type']
        self.migrate = self.mkopt('m', "Migrate This Repo",
                                  ['+', self.updateparent], val=parent['val'])
        svb = ["unique", "non-unique", "deployer"]
        behavior = ChooseList(self.scr, "Behavior", (lambda x: x), svb)
        self.behavior = self.mkopt('b', "Maven Snapshot Version Behavior",
                                   [behavior, self.updatebehavior],
                                   val=repo['behavior'])
        self.opts = [
            self.mkopt('INFO', "Repo Name (Nexus)", None, val=repo['id']),
            self.mkopt('n', "Repo Name (Artifactory)", ['|', self.fixname],
                       val=repo['id'], verif=self.chname),
            self.migrate,
            None,
            self.mkopt('INFO', "Repo Class", None, val=repo['class'],
                       verif=self.supportclass),
            self.mkopt('INFO', "Repo Type", None, val=repo['type'],
                       verif=self.supporttype),
            self.mkopt('d', "Repo Description", '|', val=repo['desc']),
            self.mkopt('l', "Repo Layout", '|', val=repo['layout'])]
        if repo['class'] in ('local', 'remote'):
            self.opts += [
                self.mkopt('r', "Handles Releases", '+', val=repo['release']),
                self.mkopt('s', "Handles Snapshots", '+', val=repo['snapshot'])]
        if repo['class'] == 'local':
            self.opts += [self.behavior]
        if repo['class'] in ('local', 'remote'):
            self.opts += [
                self.mkopt('x', "Max Unique Snapshots", '|', verif=self.chmax)]
        if repo['class'] == 'remote':
            self.opts += [
                self.mkopt('u', "Remote URL", '|', val=repo['remote'],
                           verif=self.churl)]
        self.opts += [
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def updatemigrate(self, _=None):
        self.migrate['val'] = self.parent['val']
        self.parent['stat'] = self.status()

    def updateparent(self, _=None):
        self.parent['val'] = self.migrate['val']
        self.parent['stat'] = self.status()

    def fixname(self, newname):
        if newname['val'] != None:
            newname['val'] = newname['val'].strip()
            if newname['val'] == '':
                newname['val'] = None

    def chname(self, newname):
        if newname == None:
            self.scr.msg = ('err', "Repo name cannot be blank.")
            return False
        if len(newname) > 64:
            self.scr.msg = ('err', "Repo name is too long (over 64 chars).")
            return False
        reserved = ('repo', 'list', 'api', 'ui', 'webapp', 'favicon.ico',
                    '.', '..', '&')
        if newname.lower() in reserved:
            self.scr.msg = ('err', "Repo name '" + newname + "' is reserved.")
            return False
        for c in '/\\:|?*"<>':
            if c in newname:
                self.scr.msg = ('err', "Repo name must not contain /\\:|?*\"<>")
                return False
        try:
            if newname != ET.fromstring('<' + newname + ' />').tag:
                self.scr.msg = ('err', "Repo name must be a valid xml tag.")
                return False
        except:
            self.scr.msg = ('err', "Repo name must be a valid xml tag.")
            return False
        return True

    def churl(self, newurl):
        return newurl != None

    def chmax(self, newmax):
        if newmax == None: return True
        try: maxnum = int(newmax)
        except (TypeError, ValueError): maxnum = -1
        if maxnum < 0:
            self.scr.msg = ('err', "Max must be a nonnegative integer")
        return maxnum >= 0

    def updatebehavior(self, _=None):
        self.behavior['val'] = self.behavior['act'][0].choice

    def supportclass(self, newclass):
        if newclass == 'shadow': return False
        return True

    def supporttype(self, newtype):
        return True

    def verify(self):
        verif = Menu.verify(self)
        return not self.migrate['val'] or verif

    def status(self):
        return not self.migrate['val'] or Menu.status(self)

    def applyconf(self, conf):
        behavior = None
        if "Maven Snapshot Version Behavior" in conf:
            behavior = conf["Maven Snapshot Version Behavior"]
            del conf["Maven Snapshot Version Behavior"]
        Menu.applyconf(self, conf)
        self.behavior['val'] = behavior
