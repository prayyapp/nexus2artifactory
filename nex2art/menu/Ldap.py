import logging
from ..core import Menu
from . import LdapEdit, LdapMassEdit

class Ldap(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Migrate LDAP Configs", LdapMassEdit)
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing LDAP Menu.")
        self.opts = [
            None,
            self.mkopt('e', "Edit LDAP Config", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("LDAP Menu initialized.")

    def initialize(self):
        self.log.debug("Readying LDAP Menu for display.")
        self.pagedopts = []
        for ldapn, ldap in self.scr.state[self.path].items():
            if ldap.save != True or ldap.isleaf(): continue
            if ldap["available"].data != True: continue
            path = self.path[:]
            path.extend([ldapn, "Migrate This LDAP Config"])
            self.log.debug("Readying Submenu for LDAP config '" + ldapn + "'.")
            alt = self.submenu(LdapEdit)
            self.pagedopts.append(self.mkopt(None, ldapn, '+', path=path, alt=alt))
        if len(self.pagedopts) <= 0:
            if self.scr.nexus.ldap.ldap == None:
                msg = "no connected Nexus instance"
            else: msg = "no available LDAP configs"
            self.pagedopts = [self.mkopt('INFO', msg, None)]
        self.log.debug("LDAP Menu ready for display.")
