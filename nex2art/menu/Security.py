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
        self.opts = [
            self.mkopt('u', "Users Migration Setup", self.submenu(User)),
            self.mkopt('g', "Groups Migration Setup", self.submenu(Group)),
            self.mkopt('p', "Permissions Migration Setup", self.submenu(Permission)),
            self.mkopt('l', "LDAP Migration Setup", self.submenu(Ldap)),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Security Menu initialized.")
