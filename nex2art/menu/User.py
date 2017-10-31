import logging
from ..core import Menu
from . import UserEdit

class User(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Migrate Users")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing User Menu.")
        self.opts = [
            None,
            self.mkopt('p', "Default Password", '|'),
            self.mkopt('e', "Edit User", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("User Menu initialized.")

    def initialize(self):
        self.log.debug("Readying User Menu for display.")
        self.pagedopts = []
        for usern, user in self.scr.state[self.path].items():
            if user.save != True or user.isleaf(): continue
            if user["available"].data != True: continue
            path = self.path[:]
            path.extend([usern, "Migrate This User"])
            alt = self.submenu(UserEdit)
            self.pagedopts.append(self.mkopt(None, usern, '+', path=path, alt=alt))
        if len(self.pagedopts) <= 0:
            if self.scr.nexus.security.users == None:
                msg = "no connected Nexus instance"
            else: msg = "no available users"
            self.pagedopts = [self.mkopt('INFO', msg, None)]
        self.log.debug("User Menu ready for display.")
