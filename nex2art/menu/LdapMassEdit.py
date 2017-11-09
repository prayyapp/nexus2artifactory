from ..core import Menu

class LdapMassEdit(Menu):
    def __init__(self, scr):
        self.leaf = True
        Menu.__init__(self, scr, None, "Mass Edit LDAP Config Options")
        self.opts = [
            self.mkopt('m', "Migrate This LDAP Config", '+', alt=self.massreset),
            None,
            self.mkopt('c', "Reset Field", '&'),
            self.mkopt('y', "Apply", None),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", [self.massinit, None], hdoc=False)]
        self.massinit(None)
