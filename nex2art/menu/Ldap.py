import logging
from ..core import Menu

class Ldap(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Migrate LDAP")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing LDAP Menu.")
        self.manageropts = [
            self.mkopt('INFO', "LDAP Username", None),
            self.mkopt('l', "LDAP Password", '|')]
        self.alwaysopts = [
            self.mkopt('s', "LDAP Setting Name", '|'),
            self.mkopt('g', "LDAP Group Name", '|'),
            self.mkopt('m', "Migrate LDAP", '+'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("LDAP Menu initialized.")

    def initialize(self):
        ldap = self.scr.nexus.ldap.ldap
        if ldap != None and 'managerDn' in ldap:
            self.opts = self.manageropts + self.alwaysopts
        else: self.opts = self.alwaysopts
