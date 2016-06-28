import logging
from ..core import Menu
from . import PermissionEdit

class Permission(Menu):
    def __init__(self, scr, parent):
        Menu.__init__(self, scr, "Migrate Permissions")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Permission Menu.")
        self.parent = parent
        self.optmap = {}
        self.opts = [
            None,
            self.mkopt('e', "Edit Permission", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Permission Menu initialized.")

    def initialize(self):
        self.log.debug("Readying Permission Menu for display.")
        if self.scr.nexus.security.privsdirty == False: pass
        elif self.scr.nexus.security.privs == None:
            opt = self.mkopt('INFO', "no connected Nexus instance", None)
            self.pagedopts = [opt]
        elif len(self.scr.nexus.security.privs) == 0:
            opt = self.mkopt('INFO', "no available permissions", None)
            self.pagedopts = [opt]
        else:
            self.pagedopts = []
            for priv in self.scr.nexus.security.privs.values():
                opt = self.mkopt(None, priv['name'], None, val=True)
                if priv['name'] in self.optmap:
                    alt = self.optmap[priv['name']]
                    if isinstance(alt, PermissionEdit): alt.parent = opt
                    else:
                        conf = alt
                        alt = PermissionEdit(self.scr, opt, priv, self.parent)
                        self.optmap[priv['name']] = alt
                        alt.applyconf(conf)
                    opt['alt'] = [alt]
                    alt.updateparent()
                else:
                    opt['alt'] = [PermissionEdit(self.scr, opt, priv,
                                                 self.parent)]
                    self.optmap[priv['name']] = opt['alt'][0]
                    opt['stat'] = opt['alt'][0].verify()
                opt['act'] = ['+', opt['alt'][0].updatemigrate]
                self.pagedopts.append(opt)
        self.scr.nexus.security.privsdirty = False
        self.log.debug("Permission Menu ready for display.")

    def collectconf(self):
        conf, privs = {}, []
        if self.scr.nexus.security.privs != None:
            for priv in self.scr.nexus.security.privs:
                privs.append(priv)
        for k in self.optmap:
            if isinstance(self.optmap[k], PermissionEdit):
                conf[k] = self.optmap[k].collectconf()
            else: conf[k] = self.optmap[k]
            conf[k]['available'] = k in privs
        return conf

    def applyconf(self, conf):
        self.optmap = conf
