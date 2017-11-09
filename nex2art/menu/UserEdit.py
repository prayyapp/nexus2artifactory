from ..core import Menu
from . import ItemListEdit
from . import ChooseList

class UserEdit(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Edit User Options")
        f, g, h = self.buildgroupedit, self.makegroupedit, lambda x: x['text']
        grp = self.submenu(ItemListEdit, "Groups", f, g, h)
        self.opts = [
            self.mkopt('INFO', "User Name (Nexus)", None),
            self.mkopt('n', "User Name (Artifactory)", ['|', self.fixname]),
            self.mkopt('m', "Migrate This User", '+'),
            None,
            self.mkopt('INFO', "Realm", None),
            self.mkopt('e', "Email Address", '|'),
            self.mkopt('p', "Password", '*'),
            self.mkopt('g', "Groups", grp, save=True),
            self.mkopt('a', "Is An Administrator", '+'),
            self.mkopt('d', "Is Enabled", '+'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def buildgroupedit(self, itemlist):
        tform = lambda x: x['groupName']
        groupslist = self.scr.nexus.security.roles.values()
        return [ChooseList(self.scr, None, "Group", tform, groupslist)]

    def makegroupedit(self, grp, itemlist):
        if grp == None: return False
        def nil(_): pass
        if 'groupName' in grp: grp = grp['groupName']
        for group in itemlist.pagedopts:
            if group['text'] == grp:
                msg = "This user already belongs to that group"
                self.scr.msg = ('err', msg)
                return False
        return itemlist.mkopt(None, grp, nil, alt=itemlist.delitem)

    def fixname(self, newname):
        if newname['val'] != None:
            newname['val'] = newname['val'].strip()
            if newname['val'] == '':
                newname['val'] = None

    def filt(self, filt):
        name1 = self.scr.state[self.path]["User Name (Nexus)"].data
        name2 = self.scr.state[self.path]["User Name (Artifactory)"].data
        for f in filt:
            if f not in name1 and f not in name2: return False
        return True
