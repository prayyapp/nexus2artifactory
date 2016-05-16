from ..core import Menu
from . import User
from . import Group
from . import Permission
from . import Ldap

class Security(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Migrate Security")
        self.hasldap = None
        self.users = self.mkopt('u', "Users", User(self.scr, self))
        self.groups = self.mkopt('g', "Groups", [Group(self.scr), self.refresh])
        self.opthead = [
            self.users,
            self.groups,
            self.mkopt('p', "Permissions", Permission(self.scr))]
        self.opttail = [
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.ldapmenu = self.mkopt('l', "LDAP Migration Setup", None)
        self.ldapmenu['act'][0] = Ldap(self.scr, self.ldapmenu)
        self.opts = []

    def initialize(self):
        hasldap = self.scr.nexus.ldap.ldap != None
        self.ldapmenu['act'][0].updateparent()
        if self.hasldap == hasldap: return
        self.hasldap = hasldap
        self.opts = self.opthead[:]
        if self.hasldap: self.opts.append(self.ldapmenu)
        self.opts.extend(self.opttail)

    def refresh(self, _=None):
        self.users['stat'] = self.users['act'][0].verify()
        self.scr.msg = None

    def applyconf(self, conf):
        if "LDAP Migration Setup" in conf:
            self.ldapmenu['act'][0].applyconf(conf["LDAP Migration Setup"])
            del conf["LDAP Migration Setup"]
        Menu.applyconf(self, conf)
