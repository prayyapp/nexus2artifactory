import re

class Gems(object):
    def __init__(self):
        pass

    def deployPaths(self, localpath, metapath, repo, repopath):
        parts = repopath.split('/')
        if len(parts) >= 3 and parts[-3] == 'gems':
            if parts[-1].endswith('.gem') and parts[-1].startswith(parts[-2]):
                rpath = '/'.join(parts[:-2] + parts[-1:])
                return [(localpath, metapath, repo, rpath, {})]
        return [(localpath, metapath, repo, repopath, {})]
