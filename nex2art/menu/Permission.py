import logging
from ..core import Menu
from . import PermissionEdit, PermissionMassEdit

class Permission(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Migrate Permissions", PermissionMassEdit)
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Permission Menu.")
        self.opts = [
            None,
            self.mkopt('e', "Edit Permission", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Permission Menu initialized.")

    def initialize(self):
        self.log.debug("Readying Permission Menu for display.")
        self.pagedopts = []
        for permn, perm in self.scr.state[self.path].items():
            if perm.save != True or perm.isleaf(): continue
            if perm["available"].data != True: continue
            path = self.path[:]
            path.extend([permn, "Migrate This Permission"])
            alt = self.submenu(PermissionEdit)
            self.pagedopts.append(self.mkopt(None, permn, '+', path=path, alt=alt))
        if len(self.pagedopts) <= 0:
            if self.scr.nexus.security.privs == None:
                msg = "no connected Nexus instance"
            else: msg = "no available permissions"
            self.pagedopts = [self.mkopt('INFO', msg, None)]
        self.log.debug("Permission Menu ready for display.")
