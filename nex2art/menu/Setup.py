import logging
from ..core import Menu

class Setup(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Initial Setup")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Setup Menu.")
        def nx(_): return self.scr.nexus.checkNexus()
        def ar(_): return self.scr.artifactory.checkArtifactory()
        self.opts1 = [
            self.mkopt('n', "Nexus Data Directory", ['|', nx])]
        self.nex3opts = [
            self.mkopt('x', "Nexus URL", ['|', nx]),
            self.mkopt('s', "Nexus Username", ['|', nx]),
            self.mkopt('c', "Nexus Password", ['*', nx])]
        self.opts2 = [
            None,
            self.mkopt('a', "Artifactory URL", ['|', ar]),
            self.mkopt('u', "Artifactory Username", ['|', ar]),
            self.mkopt('p', "Artifactory Password", ['*', ar]),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Setup Menu initialized.")

    def pagebuild(self):
        if self.scr.nexus.nexusversion == 3:
            self.opts = self.opts1 + self.nex3opts + self.opts2
        else: self.opts = self.opts1 + self.opts2
        Menu.pagebuild(self)
