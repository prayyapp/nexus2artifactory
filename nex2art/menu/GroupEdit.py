from ..core import Menu
from . import ItemListEdit
from . import PrivMethodEdit
from . import ChooseList

class GroupEdit(Menu):
    def __init__(self, scr, parent, group, secmenu):
        Menu.__init__(self, scr, "Edit Group Options")
        self.secmenu = secmenu
        self.parent = parent
        self.specprivs = []
        for priv in self.scr.nexus.security.allprivmap.values():
            if priv['type'] == 'view':
                name = priv['id'] + ' (view)'
                specn = (priv['id'], '(view)')
                self.specprivs.append({'name': name, 'specn': specn})
            elif priv['type'] == 'application':
                name = priv['permission'] + ' (' + priv['method'] + ')'
                specn = (priv['permission'], '(' + priv['method'] + ')')
                self.specprivs.append({'name': name, 'specn': specn})
        self.migrate = self.mkopt('m', "Migrate This Group",
                                  ['+', self.updateparent], val=parent['val'])
        perm = ItemListEdit(self.scr, None, "Permissions",
                            self.buildpermedit, self.makepermedit, None)
        self.perms = self.mkopt('p', "Permissions", perm)
        self.perms['act'][0].parent = self.perms
        def nil(_): pass
        for priv in group['privileges']:
            opt = None
            if priv['type'] == 'view':
                opt = self.mkopt(None, priv['id'], nil, val='(view)',
                                 alt=perm.delitem)
            elif priv['type'] == 'application':
                opt = self.mkopt(None, priv['permission'], nil,
                                 val='(' + priv['method'] + ')',
                                 alt=perm.delitem)
            elif priv['type'] == 'target':
                opt = self.mkopt(None, priv['privilege']['name'], None,
                                 val=priv['methods'],
                                 alt=perm.delitem, verif=self.checkdeps)
                opt['act'] = [PrivMethodEdit(self.scr, opt)]
            perm.pagedopts.append(opt)
        self.opts = [
            self.mkopt('INFO', "Group Name (Nexus)", None,
                       val=group['groupName']),
            self.mkopt('n', "Group Name (Artifactory)", ['|', self.fixname],
                       val=group['groupName'], verif=self.chname),
            self.migrate,
            None,
            self.mkopt('d', "Description", '|', val=group['description']),
            self.mkopt('j', "Auto Join Users", '+', val=False),
            self.perms,
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def buildpermedit(self, itemlist):
        tform = lambda x: x['name']
        privslist = self.scr.nexus.security.allprivs.values() + self.specprivs
        pickpriv = ChooseList(self.scr, "Permission", tform, privslist)
        methodfigure = {'val': None}
        methodedit = PrivMethodEdit(self.scr, methodfigure)
        def g(_):
            if pickpriv.choice == None: return False
            if 'specn' in pickpriv.choice: methodedit.skip = True
            for perm in self.perms['act'][0].pagedopts:
                if perm['val'] == None: vals = perm['text'],
                else: vals = perm['text'], perm['text'] + ' ' + perm['val']
                if pickpriv.choice['name'] in vals:
                    msg = "This group already has that permission"
                    self.scr.msg = ('err', msg)
                    return False
        def f(_):
            itemlist.tmpval = [pickpriv.choice, methodfigure['val']]
            methodfigure['val'] = None
            pickpriv.choice = None
            if 'specn' not in itemlist.tmpval[0]:
                if itemlist.tmpval[1] == None: return False
        return [pickpriv, g, methodedit, f]

    def makepermedit(self, _, itemlist):
        opt = None
        [priv, methods], itemlist.tmpval = itemlist.tmpval, None
        alt = itemlist.delitem
        if 'specn' in priv:
            def nil(_): pass
            name, val = priv['specn']
            opt = self.mkopt(None, name, nil, val=val, alt=alt)
        else:
            opt = self.mkopt(None, priv['name'], None, val=methods, alt=alt,
                             verif=self.checkdeps)
            opt['act'] = [PrivMethodEdit(self.scr, opt)]
        return opt

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
            self.scr.msg = ('err', "Group name cannot be blank.")
            return False
        if newname.lower() in ('.', '..', '&'):
            self.scr.msg = ('err', "Group name '" + newname + "' is reserved.")
            return False
        for c in '/\\:|?*"<>':
            if c in newname:
                self.scr.msg = ('err',
                                "Group name must not contain /\\:|?*\"<>")
                return False
        return True

    def checkdeps(self, _=None):
        conf = self.secmenu.perms['act'][0].collectconf()
        dperms = []
        for permn, perm in conf.items():
            if perm["Migrate This Permission"] == False:
                dperms.append(permn)
        for perm in self.perms['act'][0].pagedopts:
            perm['stat'] = perm['text'] not in dperms
        return None

    def verify(self):
        verif = Menu.verify(self)
        return not self.migrate['val'] or verif

    def status(self):
        return not self.migrate['val'] or Menu.status(self)
