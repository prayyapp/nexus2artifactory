import os
import xml.etree.ElementTree as ET
from . import Security, Ldap

class Nexus:
    def __init__(self):
        self.path = None
        self.repos = None
        self.repomap = None
        self.dirty = True
        self.ldap = Ldap()
        self.security = Security()

    def refresh(self, path):
        repos, repomap = [], {}
        self.path = None
        self.repos = None
        self.repomap = None
        self.dirty = True
        self.ldap.initialize()
        self.security.initialize()
        if path == None: return True
        path = os.path.abspath(path)
        config = os.path.join(path, 'conf', 'nexus.xml')
        if not os.path.isfile(config):
            return "Given path is not a valid Nexus instance."
        try:
            xml = ET.parse(config).getroot()
            self.security.gettargets(xml)
            for repo in xml.find('repositories').findall('repository'):
                repodata = {}
                repodata['id'] = repo.find('id').text
                repodata['desc'] = repo.find('name').text
                repodata['type'], repodata['layout'] = self.getPackType(repo)
                self.getRepoClass(repo, repodata)
                ext = repo.find('externalConfiguration')
                policy = None
                if ext != None: policy = ext.find('repositoryPolicy')
                repodata['release'] = False
                repodata['snapshot'] = False
                if policy != None:
                    repodata['release'] = policy.text in ('RELEASE', 'MIXED')
                    repodata['snapshot'] = policy.text in ('SNAPSHOT', 'MIXED')
                repos.append(repodata)
                repomap[repodata['id']] = repodata
        except: return "Configuration file nexus.xml is not valid."
        repos.sort(key=lambda x: x['class'])
        self.ldap.refresh(path)
        secrtn = self.security.refresh(path)
        if secrtn != True: return secrtn
        self.repos = repos
        self.repomap = repomap
        self.path = path
        return True

    def getRepoClass(self, repo, repodata):
        ext = repo.find('externalConfiguration')
        members, master = None, None
        if ext != None:
            members = ext.find('memberRepositories')
            master = ext.find('masterRepositoryId')
        remote = repo.find('remoteStorage')
        local = repo.find('localStorage')
        if local != None:
            localurl = local.find('url')
            if localurl != None:
                lurl = localurl.text
                if lurl[-1] != '/': lurl += '/'
                repodata['localurl'] = lurl
        if members != None:
            repodata['class'] = 'virtual'
            repodata['repos'] = []
            for child in members.findall('memberRepository'):
                repodata['repos'].append(child.text)
        elif remote != None:
            repodata['class'] = 'remote'
            repodata['remote'] = remote.find('url').text
        elif master != None: repodata['class'] = 'shadow'
        else: repodata['class'] = 'local'

    def getPackType(self, repo):
        rtypes = ['maven1', 'maven2', 'npm', 'nuget', 'gems']
        ltypes = ['bower', 'gradle', 'ivy', 'npm', 'nuget', 'sbt', 'vcs']
        hint = repo.find('providerHint').text
        if hint == None: return 'generic', 'simple-default'
        subs = hint[hint.rfind('-'):]
        if subs in ('-shadow', '-hosted', '-proxy', '-group'):
            hint = hint[:hint.rfind('-')]
        if hint == 'm2-m1': hint = 'maven1'
        elif hint == 'm1-m2': hint = 'maven2'
        elif hint == 'rubygems': hint = 'gems'
        if hint not in rtypes: hint = 'generic'
        layout = 'simple'
        if hint in ltypes: layout = hint
        elif hint == 'maven1': hint, layout = 'maven', 'maven-1'
        elif hint == 'maven2': hint, layout = 'maven', 'maven-2'
        return hint, layout + '-default'
