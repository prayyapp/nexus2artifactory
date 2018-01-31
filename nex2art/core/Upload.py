import os
import re
import ssl
import json
import Queue
import base64
import logging
import urllib
import urllib2
import hashlib
import threading
from . import Docker, Gitlfs, Npm, Gems

class PutRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        return 'PUT'

class Upload(object):
    def __init__(self, scr, parent):
        self.log = logging.getLogger(__name__)
        self.scr = scr
        self.parent = parent
        self.docker = Docker()
        self.gitlfs = Gitlfs()
        self.npm = Npm()
        self.gems = Gems()
        self.filelock = threading.RLock()
        self.threadct = self.scr.args.threads
        self.max_attempts = self.scr.args.retries

    def upload(self, conf):
        self.log.info("Uploading artifacts.")
        self.parent.prog.current = "Uploading artifact:"
        url, headers = self.getconndata()
        queue = Queue.Queue(2*self.threadct)
        thargs = queue, url, headers
        threads = []
        self.log.info("Creating %d threads.", self.threadct)
        for _ in xrange(self.threadct):
            t = threading.Thread(target=self.runThread, args=thargs)
            threads.append(t)
            t.start()
        self.log.info("Threads created successfully.")
        if self.scr.nexus.nexusversion == 3:
            for f in self.filelistgenerator3(conf): queue.put(f)
        else:
            for f in self.filelistgenerator2(conf): queue.put(f)
        for _ in threads: queue.put(None)
        for t in threads: t.join()
        self.log.info("All artifacts successfully uploaded.")
        self.parent.prog.stepsmap['Artifacts'][1] = True
        self.parent.prog.currentartifact = None

    def getconndata(self):
        urlp = self.parent.url
        url = urlp[0] + '://' + urlp[1] + urlp[2]
        enc = base64.b64encode(self.parent.user + ':' + self.parent.pasw)
        headers = {'User-Agent': 'nex2art', 'Authorization': "Basic " + enc}
        return url, headers

    def filelistgenerator2(self, conf):
        repomap = self.scr.nexus.repomap
        storage = os.path.join(self.scr.nexus.path, 'storage')
        for name, src in conf["Repository Migration Setup"].items():
            if not isinstance(src, dict): continue
            if src['available'] != True: continue
            if src["Migrate This Repo"] != True: continue
            if repomap and name in repomap and 'class' in repomap[name]:
                if repomap[name]['class'] != 'local': continue
            path = None
            if repomap and name in repomap and 'localurl' in repomap[name]:
                path = repomap[name]['localurl']
                path = re.sub('^file:/(.):/', '\\1:/', path)
                path = re.sub('^file:/', '/', path)
                path = os.path.abspath(path)
            else: path = os.path.join(storage, name)
            if not os.path.isdir(path): continue
            metapath = os.path.join(path, '.nexus', 'attributes')
            files = os.listdir(path)
            try: files.remove('.nexus')
            except ValueError: pass
            try: files.remove('.meta')
            except ValueError: pass
            try: files.remove('archetype-catalog.xml')
            except ValueError: pass
            while len(files) > 0:
                f = files.pop()
                if f.endswith('.md5') or f.endswith('.sha1'): continue
                ap = os.path.join(path, f)
                mp = os.path.join(metapath, f)
                if os.path.isdir(ap):
                    def joinall(x): return os.path.join(f, x)
                    files.extend(map(joinall, os.listdir(ap)))
                else: yield ap, mp, src["Repo Name (Artifactory)"]

    def filelistgenerator3(self, conf):
        repomap = self.scr.nexus.repomap
        storage = os.path.join(self.scr.nexus.path, 'blobs')
        repos, stores = [], {}
        for name, src in conf["Repository Migration Setup"].items():
            if not isinstance(src, dict): continue
            if src['available'] != True: continue
            if src["Migrate This Repo"] != True: continue
            if repomap and name in repomap:
                if 'class' in repomap[name]:
                    if repomap[name]['class'] != 'local': continue
                if 'storage' in repomap[name]:
                    repos.append(src["Repo Name (Artifactory)"])
                    store = repomap[name]['storage']
                    if store['name'] not in stores:
                        stores[store['name']] = store
                else:
                    msg = "Repo '" + name + "' does not have associated "
                    msg += "filestore, skipping artifact migration."
                    self.log.info(msg)
        for storen, store in stores.items():
            if store['type'] != 'File' or 'path' not in store:
                msg = "Filestore '" + storen + "' with type '" + store['type']
                msg += "' is not supported, skipping artifact migration."
                self.log.info(msg)
                continue
            storedir = os.path.join(storage, store['path'], 'content')
            if not os.path.isdir(storedir): continue
            for vol in os.listdir(storedir):
                if not vol.startswith('vol-'): continue
                voldir = os.path.join(storedir, vol)
                if not os.path.isdir(voldir): continue
                for chap in os.listdir(voldir):
                    if not chap.startswith('chap-'): continue
                    chapdir = os.path.join(voldir, chap)
                    if not os.path.isdir(chapdir): continue
                    for meta in os.listdir(chapdir):
                        if not meta.endswith('.properties'): continue
                        mp = os.path.join(chapdir, meta)
                        if not os.path.isfile(mp): continue
                        blob = os.path.splitext(meta)[0] + '.bytes'
                        ap = os.path.join(chapdir, blob)
                        if not os.path.isfile(ap): continue
                        yield ap, mp, repos

    def runThread(self, queue, url, headers):
        while True:
            item = queue.get()
            if item == None: break
            path, metapath, repo = item
            if self.scr.nexus.nexusversion == 3:
                locdata = self.acquireLocation3(path, metapath, repo)
                if locdata == None: continue
                repo, store = locdata
            else: store = self.acquireLocation2(path, metapath)
            paths = self.deployPaths(path, metapath, repo, store)
            for lpath, mpath, rep, rpath, props in paths:
                if self.scr.nexus.nexusversion == 3:
                    csdata = self.acquireChecksums3(lpath, mpath)
                    if csdata == None: continue
                else: csdata = self.acquireChecksums2(lpath, mpath)
                self.deploy(url, headers, props, lpath, rep, rpath, csdata)

    def deploy(self, url, headers, props, localpath, repo, repopath, csdata):
        sha2, sha1, md5 = csdata
        puturl = url + urllib.quote(repo + repopath)
        propurl = puturl
        for propn, prop in props.items():
            propurl += ';' + urllib.quote(propn, '')
            propurl += '=' + urllib.quote(prop, '')
        artifheaders = {'X-Checksum-Sha256': sha2}
        artifheaders['X-Checksum-Sha1'] = sha1
        artifheaders['X-Checksum-Md5'] = md5
        artifheaders.update(headers)
        attempt = 0
        while attempt < self.max_attempts:
            msg = "Deploying artifact checksum SHA256: %s, SHA1: %s, MD5: %s to %s. Attempt: %s"
            self.log.info(msg, sha2, sha1, md5, puturl, attempt + 1)
            stat = self.deployChecksum(propurl, artifheaders)
            if stat == 404:
                stat = self.deployArtifact(propurl, localpath, artifheaders, True)
                if stat == 409:
                    realsha1 = self.calcChecksum(hashlib.sha1(), localpath)
                    realmd5 = self.calcChecksum(hashlib.md5(), localpath)
                    if sha1 != realsha1 or md5 != realmd5:
                        msg = "Upload failed due to bad checksums, retrying."
                        self.log.info(msg)
                        artifheaders['X-Checksum-Sha1'] = realsha1
                        artifheaders['X-Checksum-Md5'] = realmd5
                        stat = self.deployArtifact(propurl, localpath, artifheaders)
            if not isinstance(stat, (int, long)) or stat < 200 or stat >= 300:
                attempt = attempt + 1
                self.log.error("Unable to deploy artifact to %s.", puturl)
            else:
                self.log.info("Successfully deployed artifact to %s.", puturl)
                self.incFileCount(repo + ':' + repopath)
                return
        self.log.error("Unable to deploy artifact to %s after %s retries.", puturl, attempt)
        self.incFileCount(repo + ':' + repopath, True)

    def deployPaths(self, localpath, metapath, repo, repopath):
        repomap = self.scr.nexus.repomap
        if repo not in repomap:
            return [(localpath, metapath, repo, repopath, {})]
        if repomap[repo]['type'] == 'docker':
            return self.docker.deployPaths(localpath, metapath, repo, repopath)
        elif repomap[repo]['type'] == 'gitlfs':
            return self.gitlfs.deployPaths(localpath, metapath, repo, repopath)
        elif repomap[repo]['type'] == 'npm' and self.scr.nexus.nexusversion == 3:
            return self.npm.deployPaths(localpath, metapath, repo, repopath)
        elif repomap[repo]['type'] == 'gems' and self.scr.nexus.nexusversion == 2:
            return self.gems.deployPaths(localpath, metapath, repo, repopath)
        return [(localpath, metapath, repo, repopath, {})]

    def deployChecksum(self, url, headers):
        chksumheaders = {'X-Checksum-Deploy': 'true'}
        chksumheaders.update(headers)
        req = PutRequest(url, headers=chksumheaders)
        try:
            if self.scr.sslnoverify:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                stat = urllib2.urlopen(req, context=ctx).getcode()
            else: stat = urllib2.urlopen(req).getcode()
        except urllib2.HTTPError as ex:
            if ex.code == 404:
                self.log.info("Artifact not found, upload required.")
            else:
                msg = "Error deploying artifact checksum:\n%s"
                self.log.exception(msg, ex.read())
            stat = ex.code
        except urllib2.URLError as ex:
            self.log.exception("Error deploying artifact checksum:")
            stat = ex.reason
        return stat

    def deployArtifact(self, url, path, headers, ignore409=False):
        stat = None
        artifactheaders = {'Content-Type': 'application/octet-stream'}
        try:
            artifactheaders['Content-Length'] = str(os.stat(path).st_size)
            artifactheaders.update(headers)
            with open(path, 'rb') as f:
                self.log.info("Uploading artifact to %s.", url)
                req = PutRequest(url, f, artifactheaders)
                try:
                    if self.scr.sslnoverify:
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE
                        stat = urllib2.urlopen(req, context=ctx).getcode()
                    else: stat = urllib2.urlopen(req).getcode()
                except urllib2.HTTPError as ex:
                    if ex.code != 409 and ignore409:
                        msg = "Error uploading artifact:\n%s"
                        self.log.exception(msg, ex.read())
                    stat = ex.code
                except urllib2.URLError as ex:
                    self.log.exception("Error uploading artifact:")
                    stat = ex.reason
        except BaseException as ex:
            self.log.exception("Error uploading artifact:")
            stat = str(ex)
        return stat

    def acquireLocation2(self, path, metapath):
        store, js = None, None
        try:
            with open(metapath, 'r') as meta: js = json.load(meta)
            store = js['storageItem-path']
        except: pass
        if store == None:
            for i, c in enumerate(path):
                if c != metapath[i]:
                    store = path[path.rfind("/", 0, i):]
                    break
        return store

    def acquireChecksums2(self, path, metapath):
        sha2, sha1, md5, js = None, None, None, None
        try:
            with open(metapath, 'r') as meta: js = json.load(meta)
            try: sha1 = js['digest.sha1']
            except: pass
            try: md5 = js['digest.md5']
            except: pass
        except: pass
        if sha1 == None:
            try:
                with open(path + '.sha1', 'r') as f: sha1 = f.read()
            except: pass
        if md5 == None:
            try:
                with open(path + '.md5', 'r') as f: md5 = f.read()
            except: pass
        sha2 = self.calcChecksum(hashlib.sha256(), path)
        if sha1 == None: sha1 = self.calcChecksum(hashlib.sha1(), path)
        if md5 == None: md5 = self.calcChecksum(hashlib.md5(), path)
        return sha2, sha1, md5

    def acquireLocation3(self, path, metapath, repos):
        repo, store, conf = None, None, self.acquireMetadata3(metapath)
        if 'deleted' in conf and conf['deleted'] == 'true': return None
        if '@Bucket.repo-name' in conf:
            repo = conf['@Bucket.repo-name']
            if repo not in repos: return None
        if '@BlobStore.blob-name' in conf:
            store = '/' + conf['@BlobStore.blob-name']
        return repo, store

    def acquireChecksums3(self, path, metapath):
        sha2, sha1, md5 = None, None, None
        conf = self.acquireMetadata3(metapath)
        if 'deleted' in conf and conf['deleted'] == 'true': return None
        sha2 = self.calcChecksum(hashlib.sha256(), path)
        if 'sha1' in conf: sha1 = conf['sha1']
        else: sha1 = self.calcChecksum(hashlib.sha1(), path)
        md5 = self.calcChecksum(hashlib.md5(), path)
        return sha2, sha1, md5

    def acquireMetadata3(self, metapath):
        conf = {}
        try:
            with open(metapath, 'r') as meta:
                for line in meta:
                    try:
                        line = line.strip()
                        if not line or line.startswith('#'): continue
                        if '=' not in line: continue
                        pair = line.split('=', 1)
                        conf[pair[0].strip()] = pair[1].strip()
                    except: pass
        except: pass
        return conf

    def calcChecksum(self, alg, path):
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''): alg.update(chunk)
            return alg.hexdigest()
        except: return None

    def incFileCount(self, fname, error=False):
        with self.filelock:
            self.parent.prog.currentartifact = fname
            self.parent.prog.stepsmap['Artifacts'][4] += 1
            if error: self.parent.prog.stepsmap['Artifacts'][3] += 1
            self.parent.prog.refresh()
