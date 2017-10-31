import logging

class Format(object):
    def __init__(self, scr):
        self.log = logging.getLogger(__name__)
        self.scr = scr

    datamodel = {
        "Initial Setup": {
            "Nexus Path": basestring,
            "Artifactory URL": basestring,
            "Artifactory Username": basestring,
            "Artifactory Password": basestring
        },
        "Repository Migration Setup": {
            None: {
                "available": bool,
                "Repo Name (Artifactory)": basestring,
                "Migrate This Repo": bool,
                "Repo Description": basestring,
                "Repo Layout": basestring,
                "Handles Releases": bool,
                "Handles Snapshots": bool,
                "Suppresses Pom Consistency Checks": bool,
                "Max Unique Snapshots": basestring,
                "Maven Snapshot Version Behavior": basestring,
                "Remote URL": basestring
            },
            "Default Max Unique Snapshots": basestring,
            "Hash All Artifacts": bool
        },
        "Security Migration Setup": {
            "Users Migration Setup": {
                None: {
                    "available": bool,
                    "User Name (Artifactory)": basestring,
                    "Migrate This User": bool,
                    "Email Address": basestring,
                    "Password": basestring,
                    "Groups": [basestring],
                    "Is An Administrator": bool,
                    "Is Enabled": bool
                },
                "Default Password": basestring
            },
            "Groups Migration Setup": {
                None: {
                    "available": bool,
                    "Group Name (Artifactory)": basestring,
                    "Migrate This Group": bool,
                    "Group Description": basestring,
                    "Auto Join Users": bool,
                    "Permissions": {None: basestring}
                }
            },
            "Permissions Migration Setup": {
                None: {
                    "available": bool,
                    "Permission Name (Artifactory)": basestring,
                    "Migrate This Permission": bool,
                    "Include Patterns": [basestring],
                    "Exclude Patterns": [basestring]
                }
            },
            "LDAP Migration Setup": {
                "available": bool,
                "LDAP Password": basestring,
                "LDAP Setting Name": basestring,
                "LDAP Group Name": basestring,
                "Migrate LDAP": bool
            }
        }
    }

    def trim(self, newtree):
        def chop(tree, model):
            if isinstance(tree, dict) and isinstance(model, dict):
                for item in tree.keys():
                    if item in model:
                        if not chop(tree[item], model[item]): del tree[item]
                    elif None in model:
                        if not chop(tree[item], model[None]): del tree[item]
                    else: del tree[item]
            elif isinstance(tree, list) and isinstance(model, list) and len(model) == 1:
                for idx, item in reversed(list(enumerate(tree))):
                    if not chop(item, model[0]): tree.pop(idx)
            elif isinstance(model, type) and (tree == None or isinstance(tree, model)): pass
            else: return False
            return True
        if not chop(newtree, self.datamodel):
            raise TypeError("Provided file is not a valid format.")
        if "Repository Migration Setup" not in newtree: return
        for repo in newtree["Repository Migration Setup"].values():
            if not isinstance(repo, dict): continue
            if "Repo Class" not in repo: continue
            repoclass = repo["Repo Class"]
            if repoclass not in ('local', 'remote'):
                if "Handles Releases" in repo: del repo["Handles Releases"]
                if "Handles Snapshots" in repo: del repo["Handles Snapshots"]
                if "Suppresses Pom Consistency Checks" in repo:
                    del repo["Suppresses Pom Consistency Checks"]
                if "Max Unique Snapshots" in repo:
                    del repo["Max Unique Snapshots"]
            if repoclass != 'local':
                if "Maven Snapshot Version Behavior" in repo:
                    del repo["Maven Snapshot Version Behavior"]
            if repoclass != 'remote':
                if "Remote URL" in repo: del repo["Remote URL"]

    def update(self):
        self.log.info("Updating data tree with Nexus data.")
        self.updaterepos()
        self.updateusers()
        self.updategroups()
        self.updateperms()
        self.updateldap()
        self.setsave()

    def updaterepos(self):
        menu = self.scr.state["Repository Migration Setup"]
        menu["Hash All Artifacts"].init(False)
        menu["Default Max Unique Snapshots"].init('0')
        for repon, repo in menu.items():
            if repo.save != True or repo.isleaf(): continue
            repo["available"].data = False
        repos = self.scr.nexus.repos
        if repos == None: return
        for repo in repos: self.updaterepo(repo, menu)

    def updaterepo(self, repo, menu):
        menu = menu[repo['id']]
        menu["available"].data = True
        menu["Repo Name (Nexus)"].data = repo['id']
        menu["Repo Name (Nexus)"].save = False
        menu["Repo Name (Artifactory)"].init(repo['id'])
        menu["Migrate This Repo"].init(True)
        menu["Repo Class"].data = repo['class']
        menu["Repo Class"].save = False
        menu["Repo Type"].data = repo['type']
        menu["Repo Type"].save = False
        menu["Repo Description"].init(repo['desc'])
        menu["Repo Layout"].init(repo['layout'])
        islocal, isremote = repo['class'] == 'local', repo['class'] == 'remote'
        isreal = islocal or isremote
        menu["Handles Releases"].init(repo['release'] if isreal else None)
        menu["Handles Releases"].save = isreal
        menu["Handles Snapshots"].init(repo['snapshot'] if isreal else None)
        menu["Handles Snapshots"].save = isreal
        menu["Suppresses Pom Consistency Checks"].init(False)
        menu["Suppresses Pom Consistency Checks"].save = isreal
        menu["Max Unique Snapshots"].init(None)
        menu["Max Unique Snapshots"].save = isreal
        menu["Maven Snapshot Version Behavior"].init(repo['behavior'] if islocal else None)
        menu["Maven Snapshot Version Behavior"].save = islocal
        menu["Remote URL"].init(repo['remote'] if isremote else None)
        menu["Remote URL"].save = isremote

    def updateusers(self):
        menu = self.scr.state["Security Migration Setup", "Users Migration Setup"]
        menu["Default Password"].init(None)
        for usern, user in menu.items():
            if user.save != True or user.isleaf(): continue
            user["available"].data = False
        users = self.scr.nexus.security.users
        if users == None: return
        for user in users.values(): self.updateuser(user, menu)

    def updateuser(self, user, menu):
        isadmin, roles = False, []
        for role in user['roles']:
            roles.append(role['groupName'])
            if role['admin']: isadmin = True
        menu = menu[user['username']]
        menu["available"].data = True
        menu["User Name (Nexus)"].data = user['username']
        menu["User Name (Nexus)"].save = False
        menu["User Name (Artifactory)"].init(user['username'])
        menu["Migrate This User"].init(True)
        menu["Realm"].data = user['realm']
        menu["Realm"].save = False
        menu["Email Address"].init(user['email'])
        menu["Password"].init(None)
        menu["Groups"].init(roles)
        menu["Is An Administrator"].init(isadmin)
        menu["Is Enabled"].init(user['enabled'])

    def updategroups(self):
        menu = self.scr.state["Security Migration Setup", "Groups Migration Setup"]
        for groupn, group in menu.items():
            if group.save != True or group.isleaf(): continue
            group["available"].data = False
        groups = self.scr.nexus.security.roles
        if groups == None: return
        for group in groups.values(): self.updategroup(group, menu)

    def updategroup(self, group, menu):
        perms = {}
        for priv in group['privileges']:
            if priv['type'] == 'view':
                perms[priv['id']] = '(view)'
            elif priv['type'] == 'application':
                perms[priv['permission']] = '(' + priv['method'] + ')'
            elif priv['type'] == 'target':
                perms[priv['privilege']['name']] = priv['methods']
        menu = menu[group['groupName']]
        menu["available"].data = True
        menu["Group Name (Nexus)"].data = group['groupName']
        menu["Group Name (Nexus)"].save = False
        menu["Group Name (Artifactory)"].init(group['groupName'])
        menu["Migrate This Group"].init(True)
        menu["Group Description"].init(group['description'])
        menu["Auto Join Users"].init(False)
        menu["Permissions"].init(perms)

    def updateperms(self):
        menu = self.scr.state["Security Migration Setup", "Permissions Migration Setup"]
        for permn, perm in menu.items():
            if perm.save != True or perm.isleaf(): continue
            perm["available"].data = False
        perms = self.scr.nexus.security.privs
        if perms == None: return
        for perm in perms.values(): self.updateperm(perm, menu)

    def updateperm(self, perm, menu):
        inc, exc = perm['target']['defincpat'], perm['target']['defexcpat']
        if inc == False: inc = []
        if exc == False: exc = []
        menu = menu[perm['name']]
        menu["available"].data = True
        menu["Permission Name (Nexus)"].data = perm['name']
        menu["Permission Name (Nexus)"].save = False
        menu["Permission Name (Artifactory)"].init(perm['name'])
        menu["Migrate This Permission"].init(True)
        menu["Repository"].data = perm['repo']
        menu["Repository"].save = False
        menu["Package Type"].data = perm['target']['ptype']
        menu["Package Type"].save = False
        menu["Nexus Regex Patterns"].data = perm['target']['patterns']
        menu["Nexus Regex Patterns"].save = False
        menu["Include Patterns"].init(inc)
        menu["Exclude Patterns"].init(exc)

    def updateldap(self):
        ldap = self.scr.nexus.ldap.ldap
        menu = self.scr.state["Security Migration Setup", "LDAP Migration Setup"]
        menu["available"].data = ldap != None
        if ldap == None: return
        menu["Migrate LDAP"].init(True)
        menu["LDAP Setting Name"].init('migratedNexusSetting')
        menu["LDAP Group Name"].init('migratedNexusGroup')
        if 'managerPassword' in ldap:
            menu["LDAP Password"].init(ldap['managerPassword'])
        if 'managerDn' in ldap:
            menu["LDAP Username"].data = ldap['managerDn']
            menu["LDAP Username"].save = False

    def setsave(self):
        self.scr.state["safety"].save = False
        self.scr.state["safety", ""].data = "WARNING!"
        self.scr.state["Save Configuration"].save = False
        self.scr.state["Load Configuration"].save = False
