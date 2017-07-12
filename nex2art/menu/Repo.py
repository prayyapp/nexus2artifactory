import logging
from ..core import Menu
from . import RepoEdit

class Repo(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Migrate Repositories")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Repo Menu.")
        self.hashall = self.mkopt('c', "Hash All Artifacts", '+', val=False)
        self.max = self.mkopt('x', "Default Max Unique Snapshots", '|',
                              val="0", verif=self.chmax)
        self.optmap = {}
        self.opts = [
            None,
            self.max,
            self.hashall,
            self.mkopt('e', "Edit Repository", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Repo Menu initialized.")

    def initialize(self):
        self.log.debug("Readying Repo Menu for display.")
        if self.scr.nexus.dirty == False: pass
        elif self.scr.nexus.repos == None:
            opt = self.mkopt('INFO', "no connected Nexus instance", None)
            self.pagedopts = [opt]
        elif len(self.scr.nexus.repos) == 0:
            opt = self.mkopt('INFO', "no available repositories", None)
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
        self.log.debug("Repo Menu ready for display.")

    def chmax(self, newmax):
        try: maxnum = int(newmax)
        except (TypeError, ValueError): maxnum = -1
        if maxnum < 0:
            self.scr.msg = ('err', "Default Max must be a nonnegative integer")
        return maxnum >= 0

    def collectconf(self):
        conf, repos = {}, []
        if self.scr.nexus.repos != None:
            for repo in self.scr.nexus.repos: repos.append(repo['id'])
        for k in self.optmap:
            if isinstance(self.optmap[k], RepoEdit):
                conf[k] = self.optmap[k].collectconf()
            else: conf[k] = self.optmap[k]
            conf[k]['available'] = k in repos
        conf["Hash All Artifacts"] = self.hashall['val']
        conf["Default Max Unique Snapshots"] = self.max['val']
        return conf

    def applyconf(self, conf):
        if "Hash All Artifacts" in conf:
            self.hashall['val'] = conf["Hash All Artifacts"]
            del conf["Hash All Artifacts"]
        if "Default Max Unique Snapshots" in conf:
            self.max['val'] = conf["Default Max Unique Snapshots"]
            del conf["Default Max Unique Snapshots"]
        self.optmap = conf
