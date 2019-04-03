import re
import json
import logging

class Npm(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def checkMeta(self, path):
        try:
            with open(path, 'r') as m:
                for line in m:
                    if line == '@BlobStore.content-type=application/json\n':
                        return True
                return False
        except: return False

    def checkContent(self, path, name):
        try:
            with open(path, 'r') as m: js = json.load(m)
            return js['name'].endswith(name)
        except: return False

    def deployPaths(self, localpath, repo, repopath):
        parts = repopath.split('/')
        if '-' in parts: return [(localpath, repo, repopath, {})]
        if self.checkMeta(metapath) and self.checkContent(localpath, parts[-1]):
            msg = "Artifactory will regenerate this metadata file"
            self.log.info("Skipping artifact %s, %s", repo + repopath, msg)
            return []
        return [(localpath, repo, repopath, {})]
