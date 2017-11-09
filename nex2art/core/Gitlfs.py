import re

class Gitlfs(object):
    def __init__(self):
        self.csrex = re.compile('^/[0-9a-f]{64}$')

    def deployPaths(self, localpath, metapath, repo, repopath):
        if self.csrex.match(repopath) == None:
            return [(localpath, metapath, repo, repopath, {})]
        s1, s2 = repopath[1:3], repopath[3:5]
        rpath = '/objects/' + s1 + '/' + s2 + repopath
        return [(localpath, metapath, repo, rpath, {})]
