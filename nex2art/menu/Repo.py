import logging
from ..core import Menu
from . import RepoEdit, RepoMassEdit

class Repo(Menu):
    def __init__(self, scr, path):
        Menu.__init__(self, scr, path, "Migrate Repositories", RepoMassEdit)
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Repo Menu.")
        self.opts = [
            None,
            self.mkopt('e', "Edit Repository", '&'),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]
        self.log.debug("Repo Menu initialized.")

    def initialize(self):
        self.log.debug("Readying Repo Menu for display.")
        self.pagedopts = []
        for repon, repo in self.scr.state[self.path].items():
            if repo.save != True or repo.isleaf(): continue
            if repo["available"].data != True: continue
            repoclass, repotype = repo["Repo Class"].data, repo["Repo Type"].data
            path = self.path[:]
            path.extend([repon, "Migrate This Repo"])
            alt = self.submenu(RepoEdit)
            opt = self.mkopt(None, repon, '+', path=path, alt=alt)
            brack = (' (', ')')
            if repoclass == 'remote': brack = (' [', ']')
            elif repoclass == 'virtual': brack = (' {', '}')
            elif repoclass == 'shadow': brack = (' <', '>')
            opt['text'] = repon + brack[0] + repotype + brack[1]
            self.pagedopts.append(opt)
        if len(self.pagedopts) <= 0:
            if self.scr.nexus.repos == None:
                msg = "no connected Nexus instance"
            else: msg = "no available repositories"
            self.pagedopts = [self.mkopt('INFO', msg, None)]
        self.log.debug("Repo Menu ready for display.")
