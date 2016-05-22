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
            if None in (self.url, self.user, self.pasw):
                msg = "Connection to Artifactory server not configured."
                raise MigrationError(msg)
            cfg = "api/system/configuration"
            conn = self.setupconn()
            artxml = self.dorequest(conn, 'GET', cfg)
            root = artxml.getroot()
            ns = root.tag[:root.tag.index('}') + 1]
            pexpire = self.enablePasswordExpire(root, ns)
            self.dorequest(conn, 'POST', cfg, artxml)
            secconf = conf["Security Migration Setup"]
            self.migraterepos(conn, conf)
            self.migrategroups(conn, secconf)
            self.migrateusers(conn, secconf)
            self.migrateperms(conn, secconf)
            artxml = self.dorequest(conn, 'GET', cfg)
            root = artxml.getroot()
            ns = root.tag[:root.tag.index('}') + 1]
            self.migrateldap(conf, root, ns)
            self.disablePasswordExpire(root, ns, pexpire)
            self.dorequest(conn, 'POST', cfg, artxml)
            self.migrateartifacts(conf)
            return True
        except MigrationError as ex: return ex.value

    def enablePasswordExpire(self, root, ns):
        exp = None
        for pol in root.iter(ns + 'expirationPolicy'): exp = pol
        enabled = exp.find(ns + 'enabled')
        cfg, enabled.text = enabled.text, 'true'
        return cfg

    def disablePasswordExpire(self, root, ns, cfg):
        exp = None
        for pol in root.iter(ns + 'expirationPolicy'): exp = pol
        enabled = exp.find(ns + 'enabled')
        enabled.text = cfg

    def migraterepos(self, conn, conf):
        cfg = 'api/repositories'
        result = self.dorequest(conn, 'GET', cfg)
        nrepos = {}
        for nrepo in self.scr.nexus.repos: nrepos[nrepo['id']] = nrepo
        repos = {}
        for res in result: repos[res['key']] = True
        for repn, rep in conf["Repository Migration Setup"].items():
            if rep['available'] != True: continue
            if rep["Migrate This Repo"] != True: continue
            nrepo = nrepos[repn]
            jsn = {}
            jsn['key'] = rep["Repo Name (Artifactory)"]
            jsn['rclass'] = nrepo['class']
            jsn['packageType'] = nrepo['type']
            jsn['description'] = rep["Description"]
            jsn['repoLayoutRef'] = rep["Repo Layout"]
            if jsn['rclass'] == 'local':
                jsn['handleReleases'] = rep["Handles Releases"]
                jsn['handleSnapshots'] = rep["Handles Snapshots"]
            if jsn['rclass'] == 'remote':
                jsn['handleReleases'] = rep["Handles Releases"]
                jsn['handleSnapshots'] = rep["Handles Snapshots"]
                jsn['url'] = rep["Remote URL"]
            if jsn['rclass'] == 'virtual':
                jsn['repositories'] = nrepo['repos']
            mthd = 'POST' if jsn['key'] in repos else 'PUT'
            cfg = 'api/repositories/' + jsn['key']
            self.dorequest(conn, mthd, cfg, jsn)

    def migrateartifacts(self, conf):
        nrepos = {}
        for nrepo in self.scr.nexus.repos: nrepos[nrepo['id']] = nrepo
        storage = os.path.join(self.scr.nexus.path, 'storage')
        url = self.url[0] + '://' + self.url[1] + self.url[2]
        for name, src in conf["Repository Migration Setup"].items():
            if src['available'] != True: continue
            if src["Migrate This Repo"] != True: continue
            if nrepos[name]['class'] != 'local': continue
            path = None
            repomap = self.scr.nexus.repomap
            if repomap and name in repomap and 'localurl' in repomap[name]:
                path = repomap[name]['localurl']
                path = re.sub('^file:/(.):/', '\\1:/', path)
                path = re.sub('^file:/', '/', path)
                path = os.path.abspath(path)
            else: path = os.path.join(storage, name)
            if not os.path.isdir(path): continue
            cmd = ['jfrog', 'rt', 'upload', '--flat=false', '--regexp=true']
            cmd.append('--user=' + str(self.user))
            cmd.append('--password=' + str(self.pasw))
            cmd.append('--url=' + str(url))
            cmd.append(str('(^[^.].*' + re.escape(os.path.sep) + ')'))
            cmd.append(str(src["Repo Name (Artifactory)"] + '/'))
            with open(os.devnull, 'w') as f:
                try: subprocess.call(cmd, cwd=path, stdout=f, stderr=f)
                except OSError as ex: raise MigrationError(str(ex))

    def migrateusers(self, conn, conf):
        defaultpasw = conf['Users']["Default Password"]
        passresets = []
        cfg = 'api/security/users'
        result = self.dorequest(conn, 'GET', cfg)
        usrs = {}
        for res in result: usrs[res['name']] = True
        if 'Users' not in conf: return
        for usern, user in conf['Users'].items():
            if not isinstance(user, dict): continue
            if user['available'] != True: continue
            if user["Migrate This User"] != True: continue
            jsn = {}
            jsn['name'] = user["User Name (Artifactory)"]
            jsn['email'] = user["Email Address"]
            if "Password" in user:
                jsn['password'] = user["Password"]
            else:
                jsn['password'] = defaultpasw
                passresets.append(jsn['name'])
            jsn['admin'] = user["Is An Administrator"]
            jsn['groups'] = []
            for group in user["Groups"]:
                if group in self.scr.nexus.security.roles:
                    jsn['groups'].append(group)
            mthd = 'POST' if jsn['name'] in usrs else 'PUT'
            cfg = 'api/security/users/' + jsn['name']
            self.dorequest(conn, mthd, cfg, jsn)
        if len(passresets) > 0:
            cfg = 'api/security/users/authorization/expirePassword'
            self.dorequest(conn, 'POST', cfg, passresets)

    def migrategroups(self, conn, conf):
        cfg = 'api/security/groups'
        result = self.dorequest(conn, 'GET', cfg)
        grps = {}
        for res in result: grps[res['name']] = True
        if 'Groups' not in conf: return
        for grpn, grp in conf['Groups'].items():
            if grp['available'] != True: continue
            if grp["Migrate This Group"] != True: continue
            jsn = {}
            jsn['name'] = grp["Group Name (Artifactory)"]
            jsn['description'] = grp["Description"]
            jsn['autoJoin'] = grp["Auto Join Users"]
            mthd = 'POST' if jsn['name'] in grps else 'PUT'
            cfg = 'api/security/groups/' + jsn['name']
            self.dorequest(conn, mthd, cfg, jsn)

    def migrateperms(self, conn, conf):
        cfg = 'api/security/permissions'
        result = self.dorequest(conn, 'GET', cfg)
        grpdata = {}
        if 'Groups' not in conf: conf['Groups'] = {}
        for grpn, grp in conf['Groups'].items():
            grpname = grp["Group Name (Artifactory)"]
            if 'Permissions' not in grp: continue
            for permn, perm in grp['Permissions'].items():
                if isinstance(perm, basestring): continue
                perms = []
                if perm["Read Permissions"]: perms.append('r')
                if perm["Create Permissions"]: perms.append('w')
                if perm["Delete Permissions"]: perms.append('d')
                if perm["Annotate Permissions"]: perms.append('n')
                if perm["Manage Permissions"]: perms.append('m')
                if permn in grpdata: grpdata[permn][grpname] = perms
                else: grpdata[permn] = {grpname: perms}
        privs = self.scr.nexus.security.privs
        if 'Permissions' not in conf: return
        for permn, perm in conf['Permissions'].items():
            if perm['available'] != True: continue
            if perm["Migrate This Permission"] != True: continue
            name = perm["Permission Name (Artifactory)"]
            incpat = ','.join(perm["Include Patterns"])
            excpat = ','.join(perm["Exclude Patterns"])
            repo = privs[name]['repo']
            if repo == '*': repo = 'ANY'
            grps = grpdata[name]
            jsn = {}
            jsn['name'] = name
            jsn['includesPattern'] = incpat
            jsn['excludesPattern'] = excpat
            jsn['repositories'] = [repo]
            jsn['principals'] = {'users': {}, 'groups': grps}
            cfg = 'api/security/permissions/' + jsn['name']
            self.dorequest(conn, 'PUT', cfg, jsn)

    def migrateldap(self, conf, root, ns):
        if "LDAP Migration Setup" not in conf["Security Migration Setup"]:
            return
        src = conf["Security Migration Setup"]["LDAP Migration Setup"]
        if src["Migrate LDAP"] == False: return
        data = self.scr.nexus.ldap.ldap
        ldap = self.buildldap(ns)
        for item in ldap.iter():
            tag = item.tag[len(ns):] if item.tag.startswith(ns) else item.tag
            if tag == 'key': item.text = src["LDAP Setting Name"]
            elif tag == 'name': item.text = src["LDAP Group Name"]
            elif tag == 'enabledLdap': item.text = src["LDAP Setting Name"]
            elif tag == 'managerPassword' and 'managerDn' in data:
                item.text = src["LDAP Password"]
            elif tag in data: item.text = data[tag]
        sec = root.find(ns + 'security')
        sets = sec.find(ns + 'ldapSettings')
        newset = ldap.find(ns + 'ldapSetting')
        ldap.remove(newset)
        key = newset.find(ns + 'key').text
        for grp in sets.findall(ns + 'ldapSetting'):
            if grp.find(ns + 'key').text == key: sets.remove(grp)
        sets.append(newset)
        if 'strategy' not in data: return
        grps = sec.find(ns + 'ldapGroupSettings')
        newgrp = ldap.find(ns + 'ldapGroupSetting')
        ldap.remove(newgrp)
        name = newgrp.find(ns + 'name').text
        for grp in grps.findall(ns + 'ldapGroupSetting'):
            if grp.find(ns + 'name').text == name: grps.remove(grp)
        grps.append(newgrp)

    def buildldap(self, ns):
        ldap = ET.Element('ldap')
        lset = ET.SubElement(ldap, ns + 'ldapSetting')
        ET.SubElement(lset, ns + 'key')
        ET.SubElement(lset, ns + 'enabled').text = 'true'
        ET.SubElement(lset, ns + 'ldapUrl')
        srch = ET.SubElement(lset, ns + 'search')
        ET.SubElement(srch, ns + 'searchFilter')
        ET.SubElement(srch, ns + 'searchBase')
        ET.SubElement(srch, ns + 'searchSubTree')
        ET.SubElement(srch, ns + 'managerDn')
        ET.SubElement(srch, ns + 'managerPassword')
        ET.SubElement(lset, ns + 'autoCreateUser').text = 'false'
        ET.SubElement(lset, ns + 'emailAttribute')
        lgrp = ET.SubElement(ldap, ns + 'ldapGroupSetting')
        ET.SubElement(lgrp, ns + 'name')
        ET.SubElement(lgrp, ns + 'groupBaseDn')
        ET.SubElement(lgrp, ns + 'groupNameAttribute')
        ET.SubElement(lgrp, ns + 'groupMemberAttribute')
        ET.SubElement(lgrp, ns + 'subTree')
        ET.SubElement(lgrp, ns + 'filter')
        ET.SubElement(lgrp, ns + 'descriptionAttribute').text = 'description'
        ET.SubElement(lgrp, ns + 'strategy')
        ET.SubElement(lgrp, ns + 'enabledLdap')
        return ldap

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
        headers = {}
        if isinstance(body, (dict, list, tuple)):
            body = json.dumps(body)
            headers['Content-Type'] = 'application/json'
        elif isinstance(body, ET.ElementTree):
            fobj = StringIO.StringIO()
            body.write(fobj)
            body = fobj.getvalue()
            fobj.close()
            headers['Content-Type'] = 'application/xml'
        builder, host, rootpath, extraheaders = conndata
        headers.update(extraheaders)
        conn = builder(host)
        conn.request(method, rootpath + path, body, headers)
        resp = conn.getresponse()
        stat, msg = resp.status, resp.read()
        ctype = resp.getheader('Content-Type', 'application/octet-stream')
        conn.close()
        if stat < 200 or stat >= 300:
            msg = "Unable to " + method + " " + path + ": " + str(stat) + "."
            raise MigrationError(msg)
        try:
            if self.json.match(ctype) != None: msg = json.loads(msg)
            elif self.xml.match(ctype) != None:
                fobj = StringIO.StringIO(msg)
                msg = ET.parse(fobj)
                fobj.close()
        except: pass
        return msg
