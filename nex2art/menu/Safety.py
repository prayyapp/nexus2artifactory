from ..core import Menu

class Safety(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, ["safety"], "Are You Sure?")
        self.discard = False
        self.opts = [
            self.mkopt('INFO', '', None),
            None,
            self.mkopt('INFO', "You have unsaved changes.", None),
            self.mkopt('INFO', "Are you sure you want to discard them?", None),
            None,
            self.mkopt('y', "Discard Changes", [self.setdiscard, None]),
            self.mkopt('n', "Cancel", None)]

    def show(self):
        self.discard = False
        Menu.show(self)
        return self.discard

    def setdiscard(self, _):
        self.discard = True
