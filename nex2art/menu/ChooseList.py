from ..core import Menu

class ChooseList(Menu):
    def __init__(self, scr, path, typ, tform, opts):
        self.leaf = True
        Menu.__init__(self, scr, path, "Choose " + typ)
        self.tform = tform
        self.chooseopts = opts
        self.pagedopts = None
        self.opts = [
            None,
            self.mkopt('q', "Back", None, hdoc=False)]

    def initialize(self):
        if self.pagedopts != None: return
        self.pagedopts = []
        for opt in self.chooseopts:
            choice = [self.setchoice(opt), None]
            popt = self.mkopt(None, self.tform(opt), choice)
            self.pagedopts.append(popt)
        self.pagedopts.sort(key=lambda x: x['text'])

    def setchoice(self, opt):
        def f(_): self.option['val'] = opt
        return f
