import os.path
import threading

class Maven(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.poms = []

    def deployPaths(self, localpath, repo, repopath):
        fname = os.path.basename(repopath)
        if fname == 'pom.xml' or fname.endswith('.pom'):
            pom = localpath, repo, repopath
            with self.lock: self.poms.append(pom)
            return []
        return [(localpath, repo, repopath, {})]

    def cleanup(self):
        for localpath, repo, repopath in self.poms:
            yield localpath, repo, repopath, {}
