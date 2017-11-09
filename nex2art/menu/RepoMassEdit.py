from ..core import Menu
from . import ChooseList

class RepoMassEdit(Menu):
    def __init__(self, scr):
        self.leaf = True
        Menu.__init__(self, scr, None, "Mass Edit Repository Options")
        title = "Maven Snapshot Version Behavior"
        svb = ["unique", "non-unique", "deployer"]
        submenu = self.submenu(ChooseList, "Behavior", (lambda x: x), svb)
        self.opts = [
            self.mkopt('m', "Migrate This Repo", '+', alt=self.massreset),
            None,
            self.mkopt('d', "Repo Description", '|', alt=self.massreset),
            self.mkopt('l', "Repo Layout", '|', alt=self.massreset),
            self.mkopt('r', "Handles Releases", '+', alt=self.massreset),
            self.mkopt('s', "Handles Snapshots", '+', alt=self.massreset),
            self.mkopt('p', "Suppresses Pom Consistency Checks", '+', alt=self.massreset),
            self.mkopt('x', "Max Unique Snapshots", '|', alt=self.massreset),
            self.mkopt('b', title, submenu, alt=self.massreset),
            self.mkopt('u', "Remote URL", '|', alt=self.massreset),
            None,
            self.mkopt('c', "Reset Field", '&'),
            self.mkopt('y', "Apply", None),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", [self.massinit, None], hdoc=False)]
        self.massinit(None)
