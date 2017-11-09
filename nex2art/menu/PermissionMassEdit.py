from ..core import Menu
from . import ItemListEdit

class PermissionMassEdit(Menu):
    def __init__(self, scr):
        self.leaf = True
        Menu.__init__(self, scr, None, "Mass Edit Permission Options")
        f, g, h = lambda _: ['|'], self.newpattern, lambda x: x['val']
        inpat = self.submenu(ItemListEdit, "Include Pattern", f, g, h)
        expat = self.submenu(ItemListEdit, "Exclude Pattern", f, g, h)
        self.opts = [
            self.mkopt('m', "Migrate This Permission", '+', alt=self.massreset),
            None,
            self.mkopt('i', "Include Patterns", inpat, alt=self.massreset),
            self.mkopt('x', "Exclude Patterns", expat, alt=self.massreset),
            None,
            self.mkopt('c', "Reset Field", '&'),
            self.mkopt('y', "Apply", None),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", [self.massinit, None], hdoc=False)]
        self.massinit(None)

    def newpattern(self, item, itemlist):
        act = ['|', itemlist.updateparent]
        return itemlist.mkopt(None, '', act, val=item, alt=itemlist.delitem)
