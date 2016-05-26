from ..core import Menu, permissionSet
from . import ItemListEdit
from . import ChooseList

class UserEdit(Menu):
    def __init__(self, scr, parent, user, secmenu):
        Menu.__init__(self, scr, "Edit User Options")
        self.secmenu = secmenu
        self.parent = parent
        self.adminprivs = []
        self.migrate = self.mkopt('m', "Migrate This User",
                                  ['+', self.updateparent], val=parent['val'])
        isadmin = False
        for role in user['roles']:
            if role['admin']: isadmin = True
        self.isadmin = self.mkopt('a', "Is An Administrator", '+', val=isadmin,
                                  verif=self.chadmin)
        self.pasw = self.mkopt('p', "Password", '*', verif=self.chpasw)
        pick = self.buildgroupedit
        create = self.makegroupedit
        grp = ItemListEdit(self.scr, None, "Groups", pick, create, None)
        self.groups = self.mkopt('g', "Groups", grp, verif=self.chprivs)
        self.groups['act'][0].parent = self.groups
        def nil(_): pass
        for group in user['roles']:
            opt = self.mkopt(None, group['groupName'], nil, alt=grp.delitem,
                             verif=self.checkdeps)
            grp.pagedopts.append(opt)
        if len(grp.pagedopts) <= 0:
            opt = self.mkopt('INFO', "no items in list", None)
            grp.pagedopts = [opt]
        self.opts = [
            self.mkopt('INFO', "User Name (Nexus)", None, val=user['username']),
            self.mkopt('n', "User Name (Artifactory)", ['|', self.fixname],
                       val=user['username'], verif=self.chname),
            self.migrate,
            None,
            self.mkopt('INFO', "Realm", None, val=user['realm']),
            self.mkopt('e', "Email Address", '|', val=user['email'],
                       verif=self.chemail),
            self.pasw,
            self.groups,
            self.isadmin,
            self.mkopt('d', "Is Enabled", '+', val=user['enabled']),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def buildgroupedit(self, itemlist):
        tform = lambda x: x['groupName']
        groupslist = self.scr.nexus.security.allroles.values()
        pickgroup = ChooseList(self.scr, "Group", tform, groupslist)
        def nil(_):
            if pickgroup.choice == None: return False
            itemlist.tmpval = pickgroup.choice
            pickgroup.choice = None
        return [pickgroup, nil]

    def makegroupedit(self, _, itemlist):
        def nil(_): pass
        grp, itemlist.tmpval = itemlist.tmpval, None
        for group in self.groups['act'][0].pagedopts:
            if group['text'] == grp['groupName']:
                msg = "This user already belongs to that group"
                self.scr.msg = ('err', msg)
                return False
        return self.mkopt(None, grp['groupName'], nil, alt=itemlist.delitem,
                          verif=self.checkdeps)

    def updatemigrate(self, _=None):
        self.migrate['val'] = self.parent['val']
        self.parent['stat'] = self.status()

    def updateparent(self, _=None):
        self.parent['val'] = self.migrate['val']
        self.parent['stat'] = self.status()

    def fixname(self, newname):
        if newname['val'] != None:
            newname['val'] = newname['val'].strip()
            if newname['val'] == '':
                newname['val'] = None

    def chname(self, newname):
        if newname == None:
            self.scr.msg = ('err', "User name cannot be blank.")
            return False
        if newname.lower() in ('.', '..', '&', 'anonymous'):
            self.scr.msg = ('err', "User name '" + newname + "' is reserved.")
            return False
        for c in '/\\:|?*"<>':
            if c in newname:
                self.scr.msg = ('err', "User name must not contain /\\:|?*\"<>")
                return False
        return True

    def chpasw(self, newpasw):
        if newpasw != None or self.isadmin['val'] == False: return True
        self.scr.msg = ('err', "Admin user must be given a password.")
        return False

    def chprivs(self, _=None):
        self.scanforadminprivs()
        if len(self.adminprivs) == 0 or self.isadmin['val'] == True:
            return self.groups['act'][0].verify()
        priv = "permission '" + self.adminprivs[0] + "'."
        self.scr.msg = ('err', "Non-admin user may not have " + priv)
        return False

    def chadmin(self, newadmin):
        self.groups['stat'] = self.chprivs()
        self.pasw['stat'] = self.chpasw(self.pasw['val'])

    def chemail(self, newemail):
        return newemail != None

    def verify(self):
        verif = Menu.verify(self)
        return not self.migrate['val'] or verif

    def status(self):
        return not self.migrate['val'] or Menu.status(self)

    def collectconf(self):
        conf = Menu.collectconf(self)
        grp = self.groups['act'][0]
        grps = []
        for group in grp.pagedopts:
            if group['key'] == 'INFO': continue
            grps.append(group['text'])
        conf['Groups'] = grps
        return conf

    def applyconf(self, conf):
        groups = conf['Groups']
        del conf['Groups']
        Menu.applyconf(self, conf)
        grp = self.groups['act'][0]
        grp.pagedopts = []
        def nil(_): pass
        for group in groups:
            opt = self.mkopt(None, group, nil, alt=grp.delitem,
                             verif=self.checkdeps)
            grp.pagedopts.append(opt)
        if len(grp.pagedopts) <= 0:
            opt = self.mkopt('INFO', "no items in list", None)
            grp.pagedopts = [opt]

    def checkdeps(self, _=None):
        conf = self.secmenu.groups['act'][0].collectconf()
        dgroups = []
        for groupn, group in conf.items():
            if group["Migrate This Group"] == False:
                dgroups.append(groupn)
        for group in self.groups['act'][0].pagedopts:
            group['stat'] = group['text'] not in dgroups
        return None

    def scanforadminprivs(self):
        privs = {}
        bgroups = self.scr.nexus.security.allroles
        cgroups = self.secmenu.groups['act'][0].collectconf()
        for grp in self.groups['act'][0].pagedopts:
            grpn = grp['text']
            if grpn in cgroups:
                grpc = cgroups[grpn]
                if 'Permissions' not in grpc: continue
                for permn, perm in grpc['Permissions'].items():
                    privs[permn] = perm
            elif grpn in bgroups:
                grpc = bgroups[grpn]
                for perm in grpc['privileges']:
                    if 'permission' in perm:
                        privs[perm['permission']] = '(' + perm['method'] + ')'
        self.adminprivs = []
        for permn, perm in privs.items():
            if permn in permissionSet and perm != '(read)':
                self.adminprivs.append(permn)
