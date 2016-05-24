from ..core import Menu
from . import UserEdit

class User(Menu):
    def __init__(self, scr, parent):
        Menu.__init__(self, scr, "Migrate Users")
        self.parent = parent
        self.pasw = self.mkopt('p', "Default Password", '|',
                               verif=self.chdefpasw)
        self.optmap = {}
        self.opts = [
            None,
            self.pasw,
            self.mkopt('e', "Edit User", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def initialize(self):
        if self.scr.nexus.security.usersdirty == False: pass
        elif self.scr.nexus.security.users == None:
            opt = self.mkopt('INFO', "no connected Nexus instance", None)
            self.pagedopts = [opt]
        elif len(self.scr.nexus.security.users) == 0:
            opt = self.mkopt('INFO', "no available users", None)
            self.pagedopts = [opt]
        else:
            self.pagedopts = []
            for user in self.scr.nexus.security.users.values():
                opt = self.mkopt(None, user['username'], None, val=True)
                if user['username'] in self.optmap:
                    alt = self.optmap[user['username']]
                    if isinstance(alt, UserEdit): alt.parent = opt
                    else:
                        conf = alt
                        alt = UserEdit(self.scr, opt, user, self.parent)
                        self.optmap[user['username']] = alt
                        alt.applyconf(conf)
                    opt['alt'] = [alt]
                    alt.updateparent()
                else:
                    opt['alt'] = [UserEdit(self.scr, opt, user, self.parent)]
                    self.optmap[user['username']] = opt['alt'][0]
                    opt['stat'] = opt['alt'][0].verify()
                opt['act'] = ['+', opt['alt'][0].updatemigrate]
                self.pagedopts.append(opt)
        self.scr.nexus.security.usersdirty = False

    def collectconf(self):
        conf, users = {}, []
        if self.scr.nexus.security.users != None:
            for user in self.scr.nexus.security.users:
                users.append(user)
        for k in self.optmap:
            if isinstance(self.optmap[k], UserEdit):
                conf[k] = self.optmap[k].collectconf()
            else: conf[k] = self.optmap[k]
            conf[k]['available'] = k in users
        conf["Default Password"] = self.pasw['val']
        return conf

    def applyconf(self, conf):
        if "Default Password" in conf:
            self.pasw['val'] = conf["Default Password"]
            del conf["Default Password"]
        self.optmap = conf

    def chdefpasw(self, newpasw):
        if newpasw != None: return True
        self.scr.msg = ('err', "Default password must not be blank.")
        return False
