from ..core import Menu

class LdapEdit(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Edit LDAP Config Options")
        self.manageropts = [
            self.mkopt('INFO', "LDAP Username", None),
            self.mkopt('l', "LDAP Password", '|')]
        self.alwaysopts = [
            self.mkopt('s', "LDAP Setting Name", '|'),
            self.mkopt('g', "LDAP Group Name", '|'),
            self.mkopt('m', "Migrate This LDAP Config", '+'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def initialize(self):
        username = self.scr.state[self.path]["LDAP Username"].data
        if username != None: self.opts = self.manageropts + self.alwaysopts
        else: self.opts = self.alwaysopts

    def filt(self, filt):
        name1 = self.scr.state[self.path]["LDAP Setting Name"].data
        name2 = self.scr.state[self.path]["LDAP Group Name"].data
        for f in filt:
            if f not in name1 and f not in name2: return False
        return True
