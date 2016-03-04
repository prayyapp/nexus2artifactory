from ..core import Menu
from . import RepoEdit

class Repo(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Migrate Repositories")
        self.optmap = {}
        self.opts = [
            None,
            self.mkopt('e', "Edit Repository", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def initialize(self):
        if self.scr.nexus.dirty == False: pass
        elif self.scr.nexus.repos == None:
            opt = self.mkopt('INFO', "no connected Nexus instance", None)
            self.pagedopts = [opt]
        elif len(self.scr.nexus.repos) == 0:
            opt = self.mkopt('INFO', "no availiable repositories", None)
            self.pagedopts = [opt]
        else:
            self.pagedopts = []
            for repo in self.scr.nexus.repos:
                brack = (' (', ')')
                if repo['class'] == 'remote': brack = (' [', ']')
                elif repo['class'] == 'virtual': brack = (' {', '}')
                elif repo['class'] == 'shadow': brack = (' <', '>')
                name = repo['id'] + brack[0] + repo['type'] + brack[1]
                opt = self.mkopt(None, name, None, val=True)
                if repo['id'] in self.optmap:
                    alt = self.optmap[repo['id']]
                    if isinstance(alt, RepoEdit): alt.parent = opt
                    else:
                        conf, alt = alt, RepoEdit(self.scr, opt, repo)
                        self.optmap[repo['id']] = alt
                        alt.applyconf(conf)
                    opt['alt'] = [alt]
                    alt.updateparent()
                else:
                    opt['alt'] = [RepoEdit(self.scr, opt, repo)]
                    self.optmap[repo['id']] = opt['alt'][0]
                    opt['stat'] = opt['alt'][0].verify()
                opt['act'] = ['+', opt['alt'][0].updatemigrate]
                self.pagedopts.append(opt)
        self.scr.nexus.dirty = False

    def collectconf(self):
        conf, repos = {}, []
        if self.scr.nexus.repos != None:
            for repo in self.scr.nexus.repos: repos.append(repo['id'])
        for k in self.optmap:
            if isinstance(self.optmap[k], RepoEdit):
                conf[k] = self.optmap[k].collectconf()
            else: conf[k] = self.optmap[k]
            conf[k]['available'] = conf[k]["Repo Name (Nexus)"] in repos
        return conf

    def applyconf(self, conf):
        self.optmap = conf
