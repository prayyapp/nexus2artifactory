import logging
from ..core import Menu
from . import User
from . import Group
from . import Permission
from . import Ldap

class Security(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Migrate Security")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Security Menu.")
        self.opthead = [
            self.mkopt('u', "Users Migration Setup", self.submenu(User)),
            self.mkopt('g', "Groups Migration Setup", self.submenu(Group)),
            self.mkopt('p', "Permissions Migration Setup", self.submenu(Permission))]
        self.opttail = [
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        path = self.path[:]
        path.extend(["LDAP Migration Setup", "Migrate LDAP"])
        self.ldapmenu = self.mkopt('l', "LDAP Migration Setup", self.submenu(Ldap), path=path)
        self.opts = []
        self.log.debug("Security Menu initialized.")

    def initialize(self):
        path = "Security Migration Setup", "LDAP Migration Setup", "available"
        hasldap = self.scr.state[path].data
        self.log.debug("Readying Security Menu for display (ldap=%s).", hasldap)
        self.opts = self.opthead[:]
        if hasldap: self.opts.append(self.ldapmenu)
        self.opts.extend(self.opttail)
        self.log.debug("Security Menu ready for display.")
