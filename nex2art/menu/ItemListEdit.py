from ..core import Menu

class ItemListEdit(Menu):
    def __init__(self, scr, path, typ, pick, create, update, readonly=False):
        self.leaf = True
        Menu.__init__(self, scr, path, typ + " List")
        self.typ = typ
        self.pick = pick
        self.create = create
        self.update = update
        self.readonly = readonly
        self.opts = []
        if not self.readonly:
            newact = self.pick(self) + [self.additem]
            self.opts += [
                None,
                self.mkopt('n', "New " + self.typ, newact),
                self.mkopt('d', "Delete " + self.typ, '&')]
        self.opts += [
            None,
            self.mkopt('q', "Back", None, hdoc=False)]

    def updateparent(self, _=None):
        if self.update == None: return
        parentval = []
        for item in self.pagedopts:
            if item['key'] == 'INFO': continue
            parentval.append(self.update(item))
        self.option['val'] = parentval
        for item in self.scr.state[self.path].values():
            for opt in self.pagedopts:
                if opt['text'] == item.data: item.valid = opt['stat']

    def initialize(self):
        if self.update == None and self.readonly == False: return
        self.pagedopts = []
        val = self.scr.state[self.path].values()
        if val != None and len(val) > 0:
            for item in val:
                opt = self.create(item.data, self)
                if opt == False: continue
                opt['stat'] = item.valid
                self.pagedopts.append(opt)
        elif isinstance(self.option['val'], list) and len(self.option['val']) > 0:
            for item in self.option['val']:
                opt = self.create(item, self)
                if opt == False: continue
                self.pagedopts.append(opt)
        if len(self.pagedopts) <= 0:
            opt = self.mkopt('INFO', "no items in list", None)
            self.pagedopts = [opt]
        self.filtpagedopts = self.pagedopts

    def additem(self, opt):
        item, opt['val'] = opt['val'], None
        opt = self.create(item, self)
        if opt == False: return False
        if len(self.pagedopts) == 1 and self.pagedopts[0]['key'] == 'INFO':
            self.pagedopts = [opt]
        else: self.pagedopts.append(opt)
        self.filtpagedopts = self.pagedopts
        self.updateparent()

    def delitem(self, opt):
        maxset = self.scr.h - len(self.opts) - len(self.motnopts) - 4
        maxset -= len(self.navopts)
        maxset = min(10, maxset)
        beg = (self.page - 1)*maxset
        end = self.page*maxset
        for idx, optc in enumerate(self.pagedopts[beg:end], beg):
            if opt is optc: del self.pagedopts[idx]
        if len(self.pagedopts) <= 0:
            opt = self.mkopt('INFO', "no items in list", None)
            self.pagedopts = [opt]
        self.filtpagedopts = self.pagedopts
        self.updateparent()
