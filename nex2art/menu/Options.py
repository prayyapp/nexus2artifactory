from ..core import Menu
from . import Ldap

class Options(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Migrate Options")
        self.hasldap = None
        self.ldapmenu = self.mkopt('l', "LDAP Migration Setup", None)
        self.ldapmenu['act'][0] = Ldap(self.scr, self.ldapmenu)
        self.opts = []

    def initialize(self):
        hasldap = self.scr.nexus.ldap != None
        self.ldapmenu['act'][0].updateparent()
        if self.hasldap == hasldap: return
        self.hasldap = hasldap
        self.opts = []
        if self.hasldap:
            self.opts += [
                self.ldapmenu,
                None]
        self.opts += [
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
