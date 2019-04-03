import re
import json
import logging
import hashlib
import threading

class Docker(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.lock = threading.Lock()
        self.csrex = re.compile('^sha256\\\\?:([0-9a-f]{64})$')
        self.mtype = 'application/vnd.docker.distribution.manifest.v2+json'
        self.discovered = {}
        self.requested = {}

    def getChecksum(self, filename):
        m = self.csrex.match(filename)
        if m == None: return None
        return m.group(1)

    def extractShas(self, manif):
        try:
            with open(manif, 'r') as m: js = json.load(m)
            yield js['config']['digest']
            for layer in js['layers']: yield layer['digest']
        except:
            self.log.exception("Error reading Docker manifest %s:", manif)

    def deployPaths(self, localpath, repo, repopath):
        parts = repopath.split('/')
        if parts[0] != '' or parts[1] != 'v2':
            yield (localpath, repo, repopath, {})
        elif (parts[2] == '-' and parts[3] == 'blobs'
                  and self.getChecksum(parts[4]) != None and len(parts) == 5):
            sha2 = self.getChecksum(parts[4])
            reqs = []
            with self.lock:
                if sha2 not in self.discovered:
                    self.discovered[sha2] = localpath
                if sha2 in self.requested:
                    reqs = self.requested[sha2]
                    del self.requested[sha2]
            for req in reqs: yield (localpath, req[0], req[1], {})
        elif (parts[-2] == 'manifests' and len(parts) > 4
                  and self.getChecksum(parts[-1]) == None):
            tagpath = '/' + '/'.join(parts[2:-2]) + '/' + parts[-1]
            props = {}
            props['docker.repoName'] = '/'.join(parts[2:-2])
            props['docker.manifest'] = parts[-1]
            props['docker.manifest.type'] = self.mtype
            manifpath = tagpath + '/manifest.json'
            yield (localpath, repo, manifpath, props)
            for layer in self.extractShas(localpath):
                sha2 = self.getChecksum(layer)
                if sha2 == None:
                    self.log.error("Skipping layer %s, not a SHA256", layer)
                    continue
                shapath, disc = tagpath + '/sha256__' + sha2, None
                with self.lock:
                    if sha2 in self.discovered: disc = self.discovered[sha2]
                    else:
                        if sha2 not in self.requested:
                            self.requested[sha2] = []
                        self.requested[sha2].append((repo, shapath))
                if disc != None: yield (disc[0], disc[1], repo, shapath, {})
        else:
            msg = "Skipping artifact %s, does not fit layout"
            self.log.info(msg, repo + repopath)
