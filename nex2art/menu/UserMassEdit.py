from ..core import Menu, DataTree
from . import ItemListEdit
from . import ChooseList

class UserMassEdit(Menu):
    def __init__(self, scr):
        self.leaf = True
        Menu.__init__(self, scr, None, "Edit User Options")
        f, g, h = self.buildgroupedit, self.makegroupedit, lambda x: x['text']
        grp = self.submenu(ItemListEdit, "Groups", f, g, h)
        self.opts = [
            self.mkopt('m', "Migrate This User", '+', alt=self.massreset),
            None,
            self.mkopt('e', "Email Address", '|', alt=self.massreset),
            self.mkopt('p', "Password", '*', alt=self.massreset),
            self.mkopt('g', "Groups", grp, alt=self.massreset),
            self.mkopt('a', "Is An Administrator", '+', alt=self.massreset),
            self.mkopt('d', "Is Enabled", '+', alt=self.massreset),
            None,
            self.mkopt('c', "Reset Field", '&'),
            self.mkopt('y', "Apply", None),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", [self.massinit, None], hdoc=False)]
        self.massinit(None)

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
