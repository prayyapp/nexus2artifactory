import logging
from ..core import Menu

class Setup(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Initial Setup")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Setup Menu.")
        self.opts = [
            self.mkopt('n', "Nexus Path", '|'),
            self.mkopt('a', "Artifactory URL", '|'),
            self.mkopt('u', "Artifactory Username", '|'),
            self.mkopt('p', "Artifactory Password", '*'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Setup Menu initialized.")
