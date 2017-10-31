from ..core import Menu
from . import ChooseList, PrivMethodEdit

# TODO this class can be simplified
class PrivMapEdit(Menu):
    def __init__(self, scr, path):
        self.leaf = True
        Menu.__init__(self, scr, path, "Permissions List")
        self.buildspecprivs()
        self.opts = [
            None,
            self.mkopt('n', "New Permission", self.buildpermedit()),
            self.mkopt('d', "Delete Permission", '&'),
            None,
            self.mkopt('q', "Back", None, hdoc=False)]

    def buildspecprivs(self):
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
        self.specmap = {}
        for priv in self.specprivs: self.specmap[priv['specn'][0]] = priv

    def updateparent(self):
        parentval = {}
        for item in self.pagedopts:
            if item['key'] == 'INFO': continue
            parentval[item['text']] = item['val']
        self.scr.state[self.path].data = parentval
        for name, item in self.scr.state[self.path].items():
            for opt in self.pagedopts:
                if opt['text'] == name: item.valid = opt['stat']

    def initialize(self):
        val = self.scr.state[self.path].items()
        if val == None or len(val) == 0:
            opt = self.mkopt('INFO', "no items in list", None)
            self.pagedopts = [opt]
        else:
            self.pagedopts = []
            for privname, methods in val:
                item = self.additem(privname, methods.data)
                if item != False: item['stat'] = methods.valid

    def additem(self, privname, methods):
        opt, alt = None, self.delitem
        if privname in self.specmap:
            def nil(_): pass
            name, val = self.specmap[privname]['specn']
            opt = self.mkopt(None, name, nil, val=val, alt=alt)
        else:
            item = [PrivMethodEdit(self.scr, None), self.updateitem]
            opt = self.mkopt(None, privname, item, val=methods, alt=alt)
        if opt == False: return False
        if len(self.pagedopts) == 1 and self.pagedopts[0]['key'] == 'INFO':
            self.pagedopts = [opt]
        else: self.pagedopts.append(opt)
        return opt

    def buildpermedit(self):
        tform = lambda x: x['name']
        privslist = self.scr.nexus.security.allprivs.values() + self.specprivs
        pickpriv = ChooseList(self.scr, None, "Permission", tform, privslist)
        methodedit = PrivMethodEdit(self.scr, None)
        privval = {}
        def g(_):
            priv = pickpriv.option['val']
            pickpriv.option['val'] = None
            if priv == None: return False
            privval['x'] = priv
            if 'specn' in priv: methodedit.skip = True
            for perm in self.pagedopts:
                if perm['val'] == None: vals = perm['text'],
                else: vals = perm['text'], perm['text'] + ' ' + perm['val']
                if priv['name'] in vals:
                    msg = "This group already has that permission"
                    self.scr.msg = ('err', msg)
                    return False
        def f(_):
            priv = privval['x']
            methods = methodedit.option['val']
            methodedit.option['val'] = None
            if 'specn' not in priv:
                if methods == None: return False
            opt, alt = None, self.delitem
            if 'specn' in priv:
                def nil(_): pass
                name, val = priv['specn']
                opt = self.mkopt(None, name, nil, val=val, alt=alt)
            else:
                item = [PrivMethodEdit(self.scr, None), self.updateitem]
                opt = self.mkopt(None, priv['name'], item, val=methods, alt=alt)
            if len(self.pagedopts) == 1 and self.pagedopts[0]['key'] == 'INFO':
                self.pagedopts = [opt]
            else: self.pagedopts.append(opt)
            self.updateparent()
        return [pickpriv, g, methodedit, f]

    def updateitem(self, opt):
        self.scr.state[self.path][opt['text']].data = opt['val']

    def delitem(self, opt):
        maxset = min(10, self.scr.h - len(self.opts) - 7)
        beg = (self.page - 1)*maxset
        end = self.page*maxset
        for idx, optc in enumerate(self.pagedopts[beg:end], beg):
            if opt is optc: del self.pagedopts[idx]
        if len(self.pagedopts) <= 0:
            opt = self.mkopt('INFO', "no items in list", None)
            self.pagedopts = [opt]
        self.updateparent()
