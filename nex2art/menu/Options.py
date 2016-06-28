import logging
from ..core import Menu

class Options(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Migrate Options")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Options Menu.")
        self.opts = [
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Options Menu initialized.")
