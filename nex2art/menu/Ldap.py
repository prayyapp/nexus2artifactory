from ..core import Menu

class Ldap(Menu):
    def __init__(self, scr, parent):
        Menu.__init__(self, scr, "Migrate LDAP")
        self.parent = parent
        self.migrate = self.mkopt('m', "Migrate LDAP", ['+', self.updateparent],
                                  val=True)
        self.useropt = self.mkopt('INFO', "LDAP Username", None)
        self.manageropts = [
            self.useropt,
            self.mkopt('l', "LDAP Password", '*', verif=self.change)]
        self.alwaysopts = [
            self.mkopt('s', "LDAP Setting Name", '|',
                       val='migratedNexusSetting', verif=self.change),
            self.mkopt('g', "LDAP Group Name", '|',
                       val='migratedNexusGroup', verif=self.change),
            self.migrate,
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        ldap = self.scr.nexus.ldap.ldap
        if ldap != None and 'managerDn' in ldap:
            self.opts = self.manageropts + self.alwaysopts
        else: self.opts = self.alwaysopts
        self.updateparent()

    def updateparent(self, _=None):
        self.parent['val'] = self.migrate['val']
        self.parent['stat'] = self.status()

    def initialize(self):
        ldap = self.scr.nexus.ldap.ldap
        if ldap != None and 'managerDn' in ldap:
            self.opts = self.manageropts + self.alwaysopts
            self.useropt['val'] = ldap['managerDn']
        else: self.opts = self.alwaysopts

    def change(self, newval):
        return newval != None

    def verify(self):
        verif = Menu.verify(self)
        return not self.migrate['val'] or verif

    def status(self):
        return not self.migrate['val'] or Menu.status(self)
