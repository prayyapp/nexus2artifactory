import logging
import ssl
import base64
import urllib2
import urlparse
import xml.etree.ElementTree as ET
from functools import wraps
from .SecConst import permissionSet

validationmap = {}

def validates(form):
    def x(f):
        validationmap[form] = f
        return f
    return x

class Validate(object):
    def __init__(self, scr):
        self.log = logging.getLogger(__name__)
        self.scr = scr
        self.validationmap = validationmap

    def __call__(self, path=[]):
        self.log.info("Validating tree from '/%s'.", '/'.join(path))
        spath, ancestors = [], []
        state = self.scr.state
        state.prune()
        for key in path:
            spath.append(key)
            state = state[key]
            ancestors.insert(0, (spath[:], state))
            if len(spath) > 0 and spath[-1] in self.validationmap: break
            if len(spath) > 1 and spath[-2] + '/.' in self.validationmap: break
        def x(p, n):
            n.valid = None
            if (n.isleaf()): n.valid = True
            elif n.islist():
                for v in sorted(n.values()):
                    pt = p[:]
                    pt.append(v.data)
                    x(pt, v)
            else:
                for k, v in sorted(n.items()):
                    pt = p[:]
                    pt.append(k)
                    x(pt, v)
            if len(p) > 0 and p[-1] in self.validationmap:
                n.valid = self.validationmap[p[-1]](self, p, n)
            elif len(p) > 1 and p[-2] + '/.' in self.validationmap:
                n.valid = self.validationmap[p[-2] + '/.'](self, p, n)
        x(spath, state)
        for p, n in ancestors[1:]:
            n.valid = None
            if len(p) > 0 and p[-1] in self.validationmap:
                n.valid = self.validationmap[p[-1]](self, p, n)
            elif len(p) > 1 and p[-2] + '/.' in self.validationmap:
                n.valid = self.validationmap[p[-2] + '/.'](self, p, n)
        self.updateStatus(state, ancestors[1:])

    def updateStatus(self, state, ancestors):
        def x(n):
            valid = True
            if n.islist():
                for v in n.values():
                    x(v)
                    if v.valid != True: valid = False
            elif not n.isleaf():
                for k, v in n.items():
                    x(v)
                    if v.valid != True: valid = False
            if n.valid == None: n.valid = valid
        x(state)
        for p, n in ancestors:
            if n.valid != None: continue
            for k, v in n.items():
                if n[k].valid != True: n.valid = False
            if n.valid == None: n.valid = True

    @validates("Default Max Unique Snapshots")
    def validateDefaultMaxUniqueSnapshots(self, path, state):
        newmax = state.data
        try: maxnum = int(newmax)
        except (TypeError, ValueError): maxnum = -1
        if maxnum < 0: return "Default Max must be a nonnegative integer"
        else: return True

    @validates("Hash All Artifacts")
    def validateHashAllArtifacts(self, path, state):
        return True

    @validates("Repository Migration Setup/.")
    def validateRepo(self, path, state):
        if state.save == False: return None
        if state["Migrate This Repo"].data: return None
        return True

    @validates("Repo Name (Artifactory)")
    def validateRepoName(self, path, state):
        newname = state.data
        if newname == None: return "Repo name cannot be blank."
        if len(newname) > 64: return "Repo name is too long (over 64 chars)."
        reserved = ('repo', 'list', 'api', 'ui', 'webapp', 'favicon.ico', '.', '..', '&')
        if newname.lower() in reserved: return "Repo name '" + newname + "' is reserved."
        for c in '/\\:|?*"<>':
            if c in newname: return "Repo name must not contain /\\:|?*\"<>"
        try:
            if newname != ET.fromstring('<' + newname + ' />').tag:
                return "Repo name must be a valid xml tag."
        except: return "Repo name must be a valid xml tag."
        return True

    @validates("Repo Class")
    def validateRepoClass(self, path, state):
        newclass = state.data
        if newclass == 'shadow': return False
        return True

    @validates("Repo Type")
    def validateRepoType(self, path, state):
        # TODO implement
        return True

    @validates("Max Unique Snapshots")
    def validateMaxUniqueSnapshots(self, path, state):
        if state.save == False: return True
        newmax = state.data
        if newmax == None: return True
        try: maxnum = int(newmax)
        except (TypeError, ValueError): maxnum = -1
        if maxnum < 0: return "Max must be a nonnegative integer"
        return True

    @validates("Remote URL")
    def validateRemoteUrl(self, path, state):
        if state.save == False: return True
        newurl = state.data
        if newurl != None: return True
        return "Remote URL must not be blank."

    @validates("Default Password")
    def validateDefaultPassword(self, path, state):
        newpasw = state.data
        if newpasw != None: return True
        return "Default password must not be blank."

    @validates("Users Migration Setup/.")
    def validateUser(self, path, state):
        if state.save == False: return None
        newpasw = state["Password"].data
        newadmin = state["Is An Administrator"].data
        if newpasw != None or newadmin == False: paswval = True
        else: paswval = "Admin user must be given a password."
        state["Password"].valid = paswval
        if state["Migrate This User"].data: return None
        return True

    @validates("User Name (Artifactory)")
    def validateUserName(self, path, state):
        newname = state.data
        if newname == None: return "User name cannot be blank."
        if newname.lower() in ('.', '..', '&', 'anonymous'):
            return "User name '" + newname + "' is reserved."
        for c in '/\\:|?*"<>':
            if c in newname: return "User name must not contain /\\:|?*\"<>"
        return True

    @validates("Email Address")
    def validateUserEmail(self, path, state):
        newemail = state.data
        if newemail == None: return "Email address must not be empty."
        return True

    @validates("Security Migration Setup")
    def validateSecuritySetup(self, path, state):
        if self.scr.nexus.security.allroles == None: return None
        perms, groups, groupadmin = [], [], []
        for permn, perm in state["Permissions Migration Setup"].items():
            if perm.isleaf(): continue
            if perm["Migrate This Permission"].data == True: continue
            perms.append(permn)
        for groupn, group in self.scr.nexus.security.allroles.items():
            for perm in group['privileges']:
                if 'permission' not in perm: continue
                if perm['permission'] in permissionSet and perm['method'] != 'read':
                    groupadmin.append(groupn)
        for groupn, group in state["Groups Migration Setup"].items():
            if group.isleaf(): continue
            admin = False
            for permn, perm in group["Permissions"].items():
                if permn in permissionSet and perm.data != "(read)":
                    admin = True
                if permn in perms:
                    perm.valid = "Specified permission is not marked for migration."
            if admin: groupadmin.append(groupn)
            if group["Migrate This Group"].data == True: continue
            groups.append(groupn)
        for usern, user in state["Users Migration Setup"].items():
            if user.isleaf(): continue
            admin = user["Is An Administrator"].data
            for group in user["Groups"].values():
                if group.data in groups:
                    group.valid = "Specified group is not marked for migration."
                elif group in groupadmin and admin == False:
                    group.valid = "Non-admin user may not have admin permission."
        return None

    @validates("Groups Migration Setup/.")
    def validateGroup(self, path, state):
        if state.save == False: return None
        if state["Migrate This Group"].data: return None
        return True

    @validates("Group Name (Artifactory)")
    def validateGroupName(self, path, state):
        newname = state.data
        if newname == None: return "Group name cannot be blank."
        if newname.lower() in ('.', '..', '&'):
            return "Group name '" + newname + "' is reserved."
        for c in '/\\:|?*"<>':
            if c in newname: return "Group name must not contain /\\:|?*\"<>"
        return True

    @validates("Permissions Migration Setup/.")
    def validatePermission(self, path, state):
        if state.save == False: return None
        if state["Migrate This Permission"].data: return None
        return True

    @validates("Permission Name (Artifactory)")
    def validatePermissionName(self, path, state):
        newname = state.data
        if newname == None: return "Permission name cannot be blank."
        return True

    @validates("Include Patterns")
    def validatePermissionPattern(self, path, state):
        newpattern = state.values()
        if len(newpattern) > 0: return True
        return "At least one include pattern must be specified."

    @validates("LDAP Migration Setup")
    def validateLDAP(self, path, state):
        if self.scr.nexus.ldap.ldap == None: return True
        if state["Migrate LDAP"].data: return None
        return True

    @validates("LDAP Password")
    def validateLDAPPassword(self, path, state):
        newpass = state.data
        if newpass != None: return True
        return "Password must not be blank."

    @validates("LDAP Setting Name")
    def validateLDAPSettingName(self, path, state):
        newsetting = state.data
        if newsetting != None: return True
        return "Setting name must not be blank."

    @validates("LDAP Group Name")
    def validateLDAPGroupName(self, path, state):
        newgroup = state.data
        if newgroup != None: return True
        return "Group name must not be blank."

    @validates("Initial Setup")
    def validateArtifactoryConnection(self, path, state):
        self.log.info("Sending system ping to Artifactory.")
        url = list(urlparse.urlparse(str(state["Artifactory URL"].data)))
        user = state["Artifactory Username"].data
        pasw = state["Artifactory Password"].data
        if url[0] not in ('http', 'https'): url = None
        elif len(url[2]) == 0 or url[2][-1] != '/': url[2] += '/'
        headers, conn, stat = {'User-Agent': 'nex2art'}, None, None
        if user != None and pasw != None:
            enc = base64.b64encode(user + ':' + pasw)
            headers['Authorization'] = "Basic " + enc
        if url != None:
            path = url[2] + 'api/system/ping'
            nurl = urlparse.urlunsplit((url[0], url[1], path, '', ''))
            self.log.info("Sending request to %s.", nurl)
            try:
                req = urllib2.Request(nurl, None, headers)
                if self.scr.sslnoverify:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    resp = urllib2.urlopen(req, context=ctx)
                else: resp = urllib2.urlopen(req)
                stat = resp.getcode()
            except urllib2.HTTPError as ex:
                msg = "Error connecting to Artifactory:\n%s"
                self.log.exception(msg, ex.read())
                stat = ex.code
            except urllib2.URLError as ex:
                self.log.exception("Error connecting to Artifactory:")
                stat = ex.reason
        valurl = state["Artifactory URL"].data == None
        valuser = user == None
        valpasw = pasw == None
        if stat in (200, 401):
            valurl = True
            self.scr.artifactory.url = url
        else: self.scr.artifactory.url = None
        if user != None and pasw != None and stat == 200:
            valuser = True
            valpasw = True
            self.scr.artifactory.user = user
            self.scr.artifactory.pasw = pasw
        else:
            self.scr.artifactory.user = None
            self.scr.artifactory.pasw = None
        if stat == 401 or (user != pasw and (user == None or pasw == None)):
            valurl = "Incorrect username and/or password."
            valuser = "Incorrect username and/or password."
            valpasw = "Incorrect username and/or password."
        elif url != None and stat != 200:
            valurl = "Unable to access Artifactory instance."
            valuser = "Unable to access Artifactory instance."
            valpasw = "Unable to access Artifactory instance."
        self.log.info("System ping completed, status: %s.", stat)
        state["Artifactory URL"].valid = valurl
        state["Artifactory Username"].valid = valuser
        state["Artifactory Password"].valid = valpasw
        val = valurl == True and valuser == True and valpasw == True
        if val != True: return False
        return None

    @validates("Nexus Path")
    def validateNexusPath(self, path, state):
        newpath = state.data
        ret = self.scr.nexus.refresh(newpath)
        self.scr.format.update()
        return ret

    @validates("safety")
    def validateSafetyMenu(self, path, state):
        return True

    @validates("")
    def validateSafetyWarning(self, path, state):
        return state.data != "WARNING!"
