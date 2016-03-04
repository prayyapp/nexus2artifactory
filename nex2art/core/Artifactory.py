import os
import re
import json
import base64
import httplib
import StringIO
import subprocess
import xml.etree.ElementTree as ET

class MigrationError(Exception):
    def __init__(self, value):
        self.value = value

class Artifactory:
    def __init__(self, scr):
        self.scr = scr
        self.json = re.compile(r'^application/(?:[^;]+\+)?json(?:;.+)?$')
        self.xml = re.compile(r'^application/(?:[^;]+\+)?xml(?:;.+)?$')
        self.url = None
        self.user = None
        self.pasw = None

    def migrate(self, conf):
        try:
            cfg = "api/system/configuration"
            if None in (self.url, self.user, self.pasw):
                msg = "Connection to Artifactory server not configured."
                raise MigrationError(msg)
            conn = self.setupconn()
            stat, artxml = self.dorequest(conn, 'GET', cfg)
            if stat != 200:
                msg = "Unable to GET /api/repositories: " + str(stat) + "."
                raise MigrationError(msg)
            root = artxml.getroot()
            ns = root.tag[:root.tag.index('}') + 1]
            self.migraterepos(conf, root, ns)
            fobj = StringIO.StringIO()
            artxml.write(fobj)
            stat, resp = self.dorequest(conn, 'POST', cfg, fobj.getvalue())
            fobj.close()
            if stat != 200:
                msg = "Unable to POST /api/repositories: " + str(stat) + "."
                raise MigrationError(msg)
            self.migrateartifacts(conf)
            return True
        except MigrationError as ex:
            return ex.value

    def migraterepos(self, conf, root, ns):
        xmlrepos = self.buildxmlmap(root, ns)
        for key, src in self.buildrepomap(conf).iteritems():
            if key in xmlrepos:
                repo, cls = xmlrepos[key]
                typ = repo.find(ns + "type")
                if typ != None: typ = typ.text
                if src["Repo Class"] != cls or src["Repo Type"] != typ:
                    msg = "Repository '" + key + "' already exists."
                    raise MigrationError(msg)
                self.updaterepo(conf, src, repo, ns)
            else:
                repo = self.buildrepo(src["Repo Class"], src["Repo Type"], ns)
                self.updaterepo(conf, src, repo, ns)
                reposet = root.find(ns + src["Repo Class"] + "Repositories")
                reposet.append(repo)

    def migrateartifacts(self, conf):
        storage = os.path.join(self.scr.nexus.path, 'storage')
        url = self.url[0] + '://' + self.url[1] + self.url[2]
        for src in conf["Repository Migration Setup"].values():
            if src['available'] != True: continue
            if src["Migrate This Repo"] != True: continue
            if src["Repo Class"] != 'local': continue
            name = src["Repo Name (Nexus)"]
            path = None
            repomap = self.scr.nexus.repomap
            if repomap and name in repomap and 'localurl' in repomap[name]:
                path = repomap[name]['localurl']
                path = re.sub('^file:/+', '/', path)
                path = os.path.abspath(path)
            else: path = os.path.join(storage, name)
            cmd = ['art', 'upload', '--flat=false', '--regexp=true']
            cmd.append('--user=' + str(self.user))
            cmd.append('--password=' + str(self.pasw))
            cmd.append('--url=' + str(url))
            cmd.append(str('(^[^.].*/)'))
            cmd.append(str(src["Repo Name (Artifactory)"] + '/'))
            with open(os.devnull, 'w') as f:
                try:
                    subprocess.call(cmd, cwd=path, stdout=f, stderr=f)
                except OSError as ex:
                    raise MigrationError(str(ex))

    def buildrepomap(self, conf):
        repomap = {}
        for src in conf["Repository Migration Setup"].values():
            if src['available'] != True: continue
            if src["Migrate This Repo"] != True: continue
            key = src["Repo Name (Artifactory)"]
            if key in repomap:
                msg = "Duplicate repository name: '" + key + "'."
                raise MigrationError(msg)
            repomap[key] = src
        return repomap

    def buildxmlmap(self, root, ns):
        xmlmap = {}
        for cls in 'local', 'remote', 'virtual':
            for repo in root.iter(ns + cls + "Repository"):
                key = repo.find(ns + 'key')
                if key != None: key = key.text
                if key != None: xmlmap[key] = repo, cls
        return xmlmap

    def updaterepo(self, conf, src, repo, ns):
        conf = conf["Repository Migration Setup"]
        attributes = (
            ('key', "Repo Name (Artifactory)"),
            ('description', "Description"),
            ('repoLayoutRef', "Repo Layout"),
            ('handleReleases', "Handles Releases"),
            ('handleSnapshots', "Handles Snapshots"),
            ('url', "Remote URL"),
            ('p2OriginalUrl', "Remote URL"))
        for akey, nkey in attributes:
            xml = repo.find(ns + akey)
            json = src[nkey] if nkey in src else None
            if xml != None:
                if json == True: xml.text = 'true'
                elif json == False: xml.text = 'false'
                else: xml.text = str(json)
        name = src["Repo Name (Nexus)"]
        nexusdata = self.scr.nexus.repomap[name]
        childlist = repo.find(ns + 'repositories')
        if childlist != None and 'repos' in nexusdata:
            childlist.clear()
            for nexname in nexusdata['repos']:
                if conf[nexname]['available'] != True: continue
                if conf[nexname]["Migrate This Repo"] != True: continue
                artname = conf[nexname]["Repo Name (Artifactory)"]
                ET.SubElement(childlist, ns + 'repositoryRef').text = artname

    def buildrepo(self, cls, typ, ns):
        repo = ET.Element(ns + cls + "Repository")
        ET.SubElement(repo, ns + 'key').text = 'temporary'
        ET.SubElement(repo, ns + 'type').text = typ
        ET.SubElement(repo, ns + 'description').text = 'temporary'
        ET.SubElement(repo, ns + 'includesPattern').text = '**/*'
        ET.SubElement(repo, ns + 'repoLayoutRef').text = 'temporary'
        ET.SubElement(repo, ns + 'dockerApiVersion').text = 'V1'
        ET.SubElement(repo, ns + 'forceDockerAuthentication').text = 'false'
        ET.SubElement(repo, ns + 'forceNugetAuthentication').text = 'false'
        if cls in ('local', 'remote'):
            ET.SubElement(repo, ns + 'blackedOut').text = 'false'
            ET.SubElement(repo, ns + 'handleReleases').text = 'true'
            ET.SubElement(repo, ns + 'handleSnapshots').text = 'true'
            ET.SubElement(repo, ns + 'maxUniqueSnapshots').text = '0'
            spcc = 'false' if typ == 'maven' else 'true'
            ET.SubElement(repo, ns + 'suppressPomConsistencyChecks').text = spcc
            ps = ET.SubElement(repo, ns + 'propertySets')
            ET.SubElement(ps, ns + 'propertySetRef').text = 'artifactory'
            ET.SubElement(repo, ns + 'archiveBrowsingEnabled').text = 'false'
        if cls == 'local':
            ET.SubElement(repo, ns + 'snapshotVersionBehavior').text = 'unique'
            lrcpt = 'localRepoChecksumPolicyType'
            ET.SubElement(repo, ns + lrcpt).text = 'client-checksums'
            cym = 'true' if typ == 'yum' else 'false'
            ET.SubElement(repo, ns + 'calculateYumMetadata').text = cym
            ET.SubElement(repo, ns + 'yumRootDepth').text = '0'
            if typ == 'yum':
                ygfn = 'yumGroupFileNames'
                ET.SubElement(repo, ns + ygfn).text = 'groups.xml'
            ET.SubElement(repo, ns + 'debianTrivialLayout').text = 'false'
        if cls == 'remote':
            ET.SubElement(repo, ns + 'url').text = 'temporary'
            ET.SubElement(repo, ns + 'offline').text = 'false'
            ET.SubElement(repo, ns + 'hardFail').text = 'false'
            ET.SubElement(repo, ns + 'storeArtifactsLocally').text = 'true'
            ET.SubElement(repo, ns + 'fetchJarsEagerly').text = 'false'
            ET.SubElement(repo, ns + 'fetchSourcesEagerly').text = 'false'
            ET.SubElement(repo, ns + 'retrievalCachePeriodSecs').text = '600'
            ET.SubElement(repo, ns + 'assumedOfflinePeriodSecs').text = '300'
            mrcps = 'missedRetrievalCachePeriodSecs'
            ET.SubElement(repo, ns + mrcps).text = '1800'
            rrcpt = 'remoteRepoChecksumPolicyType'
            ET.SubElement(repo, ns + rrcpt).text = 'generate-if-absent'
            uacph = 'unusedArtifactsCleanupPeriodHours'
            ET.SubElement(repo, ns + uacph).text = '0'
            ET.SubElement(repo, ns + 'shareConfiguration').text = 'false'
            ET.SubElement(repo, ns + 'synchronizeProperties').text = 'false'
            lrfi = 'false' if typ in ('npm', 'nuget', 'gems') else 'true'
            ET.SubElement(repo, ns + 'listRemoteFolderItems').text = lrfi
            ET.SubElement(repo, ns + 'rejectInvalidJars').text = 'false'
            if typ in ('maven', 'ivy', 'gradle', 'sbt', 'p2'):
                ET.SubElement(repo, ns + 'p2OriginalUrl').text = 'temporary'
            if typ == 'nuget':
                nu = ET.SubElement(repo, ns + 'nuget')
                ET.SubElement(nu, ns + 'feedContextPath').text = 'api/v2'
                dcp = 'downloadContextPath'
                ET.SubElement(nu, ns + dcp).text = 'api/v2/package'
            cs = ET.SubElement(repo, ns + 'contentSynchronisation')
            ET.SubElement(cs, ns + 'enabled').text = 'false'
            stat = ET.SubElement(cs, ns + 'statistics')
            ET.SubElement(stat, ns + 'enabled').text = 'false'
            prop = ET.SubElement(cs, ns + 'properties')
            ET.SubElement(prop, ns + 'enabled').text = 'false'
            sorc = ET.SubElement(cs, ns + 'source')
            ET.SubElement(sorc, ns + 'originAbsenceDetection').text = 'false'
            ET.SubElement(repo, ns + 'allowAnyHostAuth').text = 'false'
            ET.SubElement(repo, ns + 'socketTimeoutMillis').text = '15000'
            ET.SubElement(repo, ns + 'enableCookieManagement').text = 'false'
            ET.SubElement(repo, ns + 'enableTokenAuthentication').text = 'false'
            ET.SubElement(repo, ns + 'propagateQueryParams').text = 'false'
        if cls == 'virtual':
            arcrra = 'artifactoryRequestsCanRetrieveRemoteArtifacts'
            ET.SubElement(repo, ns + arcrra).text = 'false'
            ET.SubElement(repo, ns + 'repositories')
            prrcp = 'pomRepositoryReferencesCleanupPolicy'
            ET.SubElement(repo, ns + prrcp).text = 'discard_active_reference'
            if typ == 'npm':
                exd = ET.SubElement(repo, ns + 'externalDependencies')
                ET.SubElement(exd, ns + 'enabled').text = 'false'
                pat = ET.SubElement(exd, ns + 'patterns')
                ET.SubElement(pat, ns + 'pattern').text = '**'
            if typ == 'p2':
                p2 = ET.SubElement(repo, ns + 'p2')
                ET.SubElement(p2, ns + 'urls')
        return repo

    def setupconn(self):
        headers = {'User-Agent': 'nex2art'}
        enc = base64.b64encode(self.user + ':' + self.pasw)
        headers['Authorization'] = "Basic " + enc
        builder = None
        if self.url[0] == 'https': builder = httplib.HTTPSConnection
        elif self.url[0] == 'http': builder = httplib.HTTPConnection
        return builder, self.url[1], self.url[2], headers

    def dorequest(self, conndata, method, path, body=None):
        stat, msg, ctype = None, None, None
        builder, host, rootpath, headers = conndata
        try:
            conn = builder(host)
            conn.request(method, rootpath + path, body, headers)
            resp = conn.getresponse()
            stat, msg = resp.status, resp.read()
            ctype = resp.getheader('Content-Type', 'application/octet-stream')
            conn.close()
        except: return None, None
        try:
            if self.json.match(ctype) != None:
                msg = json.loads(msg)
            elif self.xml.match(ctype) != None:
                fobj = StringIO.StringIO(msg)
                msg = ET.parse(fobj)
                fobj.close()
        except: pass
        return stat, msg
