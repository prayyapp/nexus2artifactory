from ..core import Menu
from . import ChooseList

class RepoEdit(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Edit Repository Options")
        self.allopts = [
            self.mkopt('INFO', "Repo Name (Nexus)", None),
            self.mkopt('n', "Repo Name (Artifactory)", ['|', self.fixname]),
            self.mkopt('m', "Migrate This Repo", '+'),
            None,
            self.mkopt('INFO', "Repo Class", None),
            self.mkopt('INFO', "Repo Type", None),
            self.mkopt('d', "Repo Description", '|'),
            self.mkopt('l', "Repo Layout", '|')]
        self.realopts = [
            self.mkopt('r', "Handles Releases", '+'),
            self.mkopt('s', "Handles Snapshots", '+'),
            self.mkopt('p', "Suppresses Pom Consistency Checks", '+'),
            self.mkopt('x', "Max Unique Snapshots", '|')]
        title = "Maven Snapshot Version Behavior"
        svb = ["unique", "non-unique", "deployer"]
        submenu = self.submenu(ChooseList, "Behavior", (lambda x: x), svb)
        self.localopts = [self.mkopt('b', title, submenu, save=True)]
        self.remoteopts = [self.mkopt('u', "Remote URL", '|')]
        self.postopts = [
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def initialize(self):
        repoclass = self.scr.state[self.path]["Repo Class"].data
        self.opts = self.allopts[:]
        if repoclass in ('local', 'remote'): self.opts.extend(self.realopts)
        if repoclass == 'local': self.opts.extend(self.localopts)
        if repoclass == 'remote': self.opts.extend(self.remoteopts)
        self.opts.extend(self.postopts)

    def fixname(self, newname):
        if newname['val'] != None:
            newname['val'] = newname['val'].strip()
            if newname['val'] == '':
                newname['val'] = None
