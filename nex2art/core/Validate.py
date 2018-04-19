import logging
import ssl
import base64
import urllib2
import urlparse
import xml.etree.ElementTree as ET
from functools import wraps

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

    @validates("Repository Migration Setup/.")
    def validateRepo(self, path, state):
        if state.save == False or state.isleaf(): return None
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
        newtype = state.data
        if newtype == 'bower': return False
        return True

    @validates("Max Unique Snapshots")
    def validateMaxUniqueSnapshots(self, path, state):
        if state.save == False: return True
        newmax = state.data
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

    @validates("Users Migration Setup")
    def validateDefaultPassword(self, path, state):
        newpasw = state["Default Password"]
        if newpasw.data != None:
            newpasw.valid = True
            return None
        for usern, user in state.items():
            if user.save == False or user.isleaf(): continue
            if user["available"].data != True: continue
            if user["Migrate This User"].data != True: continue
            if user["Is An Administrator"].data == True: continue
            if user["Password"].data != None: continue
            newpasw.valid = "Default password must not be blank."
            return None
        newpasw.valid = True
        return None

    @validates("Users Migration Setup/.")
    def validateUser(self, path, state):
        if state.save == False or state.isleaf(): return None
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
        if self.scr.nexus.security.roles == None: return None
        privmap = self.scr.nexus.security.privmap
        perms, groups, groupadmin = [], [], []
        for permn, perm in state["Permissions Migration Setup"].items():
            if perm.isleaf(): continue
            if perm["Migrate This Permission"].data == True: continue
            perms.append(permn)
        for groupn, group in self.scr.nexus.security.roles.items():
            for perm in group['privileges']:
                if perm['needadmin']: groupadmin.append(groupn)
        for groupn, group in state["Groups Migration Setup"].items():
            if group.isleaf(): continue
            admin = False
            for permn, perm in group["Permissions"].items():
                if permn in privmap and privmap[permn]['needadmin']:
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
                elif group.data in groupadmin and admin == False:
                    group.valid = "Non-admin user may not have admin permission."
        return None

    @validates("Groups Migration Setup/.")
    def validateGroup(self, path, state):
        if state.save == False or state.isleaf(): return None
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
        if state.save == False or state.isleaf(): return None
        if path[-1] != None:
            priv = self.scr.nexus.security.privs[path[-1]]
            incp, excp = priv['defincpat'], priv['defexcpat']
            includepat = state["Include Patterns"]
            excludepat = state["Exclude Patterns"]
            resetpat = state["Reset Patterns"]
            if len(includepat.values()) + len(excludepat.values()) <= 0:
                msg = "Unable to generate default patterns"
                if incp == False: resetpat.valid = msg + '.'
                else: resetpat.valid = msg + ': ' + incp
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

    @validates("LDAP Migration Setup/.")
    def validateLDAP(self, path, state):
        if state.save == False or state.isleaf(): return None
        if state["Migrate This LDAP Config"].data: return None
        return True

    @validates("LDAP Password")
    def validateLDAPPassword(self, path, state):
        if state.save == False: return True
        if state.data != None: return True
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
    def validateConnections(self, path, state):
        state["Artifactory URL"].valid = self.scr.artifactory.vurl
        state["Artifactory Username"].valid = self.scr.artifactory.vuser
        state["Artifactory Password"].valid = self.scr.artifactory.vpasw
        state["Nexus Data Directory"].valid = self.scr.nexus.vpath
        state["Nexus URL"].valid = self.scr.nexus.vurl
        state["Nexus Username"].valid = self.scr.nexus.vuser
        state["Nexus Password"].valid = self.scr.nexus.vpasw
        return None

    @validates("Save Config JSON File")
    def validateSaveConfig(self, path, state):
        return self.scr.savest

    @validates("Load Config JSON File")
    def validateLoadConfig(self, path, state):
        return self.scr.loadst

    @validates("safety")
    def validateSafetyMenu(self, path, state):
        return True

    @validates("")
    def validateSafetyWarning(self, path, state):
        return state.data != "WARNING!"
