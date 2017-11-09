from ..core import Menu
from . import PrivMapEdit

class GroupEdit(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Edit Group Options")
        self.opts = [
            self.mkopt('INFO', "Group Name (Nexus)", None),
            self.mkopt('n', "Group Name (Artifactory)", ['|', self.fixname]),
            self.mkopt('m', "Migrate This Group", '+'),
            None,
            self.mkopt('d', "Group Description", '|'),
            self.mkopt('j', "Auto Join Users", '+'),
            self.mkopt('p', "Permissions", self.submenu(PrivMapEdit), save=True),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def fixname(self, newname):
        if newname['val'] != None:
            newname['val'] = newname['val'].strip()
            if newname['val'] == '':
                newname['val'] = None

    def filt(self, filt):
        name1 = self.scr.state[self.path]["Group Name (Nexus)"].data
        name2 = self.scr.state[self.path]["Group Name (Artifactory)"].data
        for f in filt:
            if f not in name1 and f not in name2: return False
        return True
