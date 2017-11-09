from ..core import Menu
from . import ItemListEdit

class PermissionEdit(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Edit Permission Options")
        f, g, h = lambda _: ['|'], self.newpattern, lambda x: x['val']
        rxpat = self.submenu(ItemListEdit, "Nexus Pattern", None, self.newregex, None, readonly=True)
        inpat = self.submenu(ItemListEdit, "Include Pattern", f, g, h)
        expat = self.submenu(ItemListEdit, "Exclude Pattern", f, g, h)
        self.opts = [
            self.mkopt('INFO', "Permission Name (Nexus)", None),
            self.mkopt('n', "Permission Name (Artifactory)", ['|', self.fixname]),
            self.mkopt('m', "Migrate This Permission", '+'),
            None,
            self.mkopt('INFO', "Repository", None),
            self.mkopt('INFO', "Package Type", None),
            self.mkopt('p', "Nexus Regex Patterns", rxpat, save=False),
            self.mkopt('i', "Include Patterns", inpat, save=True),
            self.mkopt('x', "Exclude Patterns", expat, save=True),
            self.mkopt('r', "Reset Patterns", self.resetpatterns, save=False),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def newpattern(self, item, itemlist):
        act = ['|', itemlist.updateparent]
        return itemlist.mkopt(None, '', act, val=item, alt=itemlist.delitem)

    def newregex(self, item, itemlist):
        def idact(_): pass
        return itemlist.mkopt(None, '', idact, val=item)

    def resetpatterns(self, _=None):
        noDefault = False
        priv = self.scr.nexus.security.privs[self.path[-1]]
        incp, excp = priv['defincpat'], priv['defexcpat']
        includepat = self.scr.state[self.path]["Include Patterns"]
        excludepat = self.scr.state[self.path]["Exclude Patterns"]
        if incp == False: noDefault, incp = True, []
        if excp == False: noDefault, excp = True, []
        includepat.data, excludepat.data = incp, excp
        if noDefault: includepat.valid = "Unable to generate default patterns."

    def fixname(self, newname):
        if newname['val'] != None:
            newname['val'] = newname['val'].strip()
            if newname['val'] == '':
                newname['val'] = None

    def filt(self, filt):
        name1 = self.scr.state[self.path]["Permission Name (Nexus)"].data
        name1 = self.scr.state[self.path]["Permission Name (Artifactory)"].data
        for f in filt:
            if f not in name1 and f not in name2: return False
        return True
