from ..core import Menu
from . import PrivMapEdit

class GroupMassEdit(Menu):
    def __init__(self, scr):
        self.leaf = True
        Menu.__init__(self, scr, None, "Edit Group Options")
        self.opts = [
            self.mkopt('m', "Migrate This Group", '+', alt=self.massreset),
            None,
            self.mkopt('d', "Group Description", '|', alt=self.massreset),
            self.mkopt('j', "Auto Join Users", '+', alt=self.massreset),
            # self.mkopt('p', "Permissions", self.submenu(PrivMapEdit), alt=self.massreset),
            None,
            self.mkopt('c', "Reset Field", '&'),
            self.mkopt('y', "Apply", None),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", [self.massinit, None], hdoc=False)]
        self.massinit(None)
