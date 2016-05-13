from ..core import Menu
from . import GroupEdit

class Group(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Migrate Groups")
        self.optmap = {}
        self.opts = [
            None,
            self.mkopt('e', "Edit Group", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def initialize(self):
        if self.scr.nexus.security.rolesdirty == False: pass
        elif self.scr.nexus.security.roles == None:
            opt = self.mkopt('INFO', "no connected Nexus instance", None)
            self.pagedopts = [opt]
        elif len(self.scr.nexus.security.roles) == 0:
            opt = self.mkopt('INFO', "no available groups", None)
            self.pagedopts = [opt]
        else:
            self.pagedopts = []
            for group in self.scr.nexus.security.roles.values():
                opt = self.mkopt(None, group['groupName'], None, val=True)
                if group['groupName'] in self.optmap:
                    alt = self.optmap[group['groupName']]
                    if isinstance(alt, GroupEdit): alt.parent = opt
                    else:
                        conf, alt = alt, GroupEdit(self.scr, opt, group)
                        self.optmap[group['groupName']] = alt
                        alt.applyconf(conf)
                    opt['alt'] = [alt]
                    alt.updateparent()
                else:
                    opt['alt'] = [GroupEdit(self.scr, opt, group)]
                    self.optmap[group['groupName']] = opt['alt'][0]
                    opt['stat'] = opt['alt'][0].verify()
                opt['act'] = ['+', opt['alt'][0].updatemigrate]
                self.pagedopts.append(opt)
        self.scr.nexus.security.rolesdirty = False

    def collectconf(self):
        conf, groups = {}, []
        if self.scr.nexus.security.roles != None:
            for group in self.scr.nexus.security.roles:
                groups.append(group)
        for k in self.optmap:
            if isinstance(self.optmap[k], GroupEdit):
                conf[k] = self.optmap[k].collectconf()
            else: conf[k] = self.optmap[k]
            conf[k]['available'] = k in groups
        return conf

    def applyconf(self, conf):
        self.optmap = conf
