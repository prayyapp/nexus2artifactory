from ..core import Menu

class Options(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Migrate Options")
        self.opts = [
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
