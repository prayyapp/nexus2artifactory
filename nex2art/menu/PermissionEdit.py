from ..core import Menu
from . import ItemListEdit
from . import ChooseList

class PermissionEdit(Menu):
    def __init__(self, scr, parent, priv, secmenu):
        Menu.__init__(self, scr, "Edit Permission Options")
        self.secmenu = secmenu
        self.parent = parent
        targ = priv['target']
        rxpat = ItemListEdit(self.scr, None, "Nexus Pattern", None,
                             self.newregex, None, readonly=True)
        inpat = ItemListEdit(self.scr, None, "Include Pattern", lambda _: ['|'],
                             self.newpattern, lambda x: x['val'])
        expat = ItemListEdit(self.scr, None, "Exclude Pattern", lambda _: ['|'],
                             self.newpattern, lambda x: x['val'])
        self.migrate = self.mkopt('m', "Migrate This Permission",
                                  ['+', self.updateparent], val=parent['val'])
        self.regexpat = self.mkopt('p', "Nexus Regex Patterns",
                                   rxpat, val=targ['patterns'], save=False)
        self.includepat = self.mkopt('i', "Include Patterns", inpat,
                                     verif=self.chpattern)
        self.excludepat = self.mkopt('x', "Exclude Patterns", expat)
        self.regexpat['act'][0].parent = self.regexpat
        self.includepat['act'][0].parent = self.includepat
        self.excludepat['act'][0].parent = self.excludepat
        self.defincpat = targ['defincpat']
        self.defexcpat = targ['defexcpat']
        self.resetpatterns()
        self.opts = [
            self.mkopt('INFO', "Permission Name (Nexus)", None,
                       val=priv['name']),
            self.mkopt('n', "Permission Name (Artifactory)",
                       ['|', self.fixname],
                       val=priv['name'], verif=self.chname),
            self.migrate,
            None,
            self.mkopt('INFO', "Repository", None, val=priv['repo']),
            self.mkopt('INFO', "Package Type", None, val=targ['ptype']),
            self.regexpat,
            self.includepat,
            self.excludepat,
            self.mkopt('r', "Reset Patterns", self.resetpatterns),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def chpattern(self, newpattern):
        return self.includepat['val'] != []

    def newpattern(self, item, itemlist):
        act = ['|', itemlist.updateparent]
        return self.mkopt(None, '', act, val=item, alt=itemlist.delitem)

    def newregex(self, item, itemlist):
        def idact(_): pass
        act = idact
        return self.mkopt(None, '', act, val=item)

    def resetpatterns(self, _=None):
        noDefault = False
        incp, excp = self.defincpat, self.defexcpat
        if incp == False: noDefault, incp = True, []
        if excp == False: noDefault, excp = True, []
        self.includepat['val'], self.excludepat['val'] = incp, excp
        if noDefault:
            self.includepat['stat'] = False
            self.scr.msg = ('err', "Unable to generate default patterns.")

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
            self.scr.msg = ('err', "Permission name cannot be blank.")
            return False
        return True

    def verify(self):
        verif = Menu.verify(self)
        return not self.migrate['val'] or verif

    def status(self):
        return not self.migrate['val'] or Menu.status(self)

    def collectconf(self):
        conf = Menu.collectconf(self)
        if isinstance(conf['Include Patterns'], dict):
            conf['Include Patterns'] = conf['Include Patterns'].values()
        if isinstance(conf['Exclude Patterns'], dict):
            conf['Exclude Patterns'] = conf['Exclude Patterns'].values()
        return conf

    def applyconf(self, conf):
        inc = conf['Include Patterns']
        exc = conf['Exclude Patterns']
        del conf['Include Patterns']
        del conf['Exclude Patterns']
        Menu.applyconf(self, conf)
        self.includepat['val'] = inc
        self.excludepat['val'] = exc
