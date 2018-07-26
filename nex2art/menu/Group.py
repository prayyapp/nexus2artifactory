import logging
from ..core import Menu
from . import GroupEdit, GroupMassEdit

class Group(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Migrate Groups", GroupMassEdit)
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Group Menu.")
        self.opts = [
            None,
            self.mkopt('e', "Edit Group", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Group Menu initialized.")

    def initialize(self):
        self.log.debug("Readying Group Menu for display.")
        self.pagedopts = []
        for groupn, group in self.scr.state[self.path].items():
            if group.save != True or group.isleaf(): continue
            if group["available"].data != True: continue
            path = self.path[:]
            path.extend([groupn, "Migrate This Group"])
            self.log.debug("Readying Submenu for group '" + groupn + "'.")
            alt = self.submenu(GroupEdit)
            self.pagedopts.append(self.mkopt(None, groupn, '+', path=path, alt=alt))
        if len(self.pagedopts) <= 0:
            if self.scr.nexus.security.roles == None:
                msg = "no connected Nexus instance"
            else: msg = "no available groups"
            self.pagedopts = [self.mkopt('INFO', msg, None)]
        self.log.debug("Group Menu ready for display.")
