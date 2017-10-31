from ..core import Menu

class ChooseList(Menu):
    def __init__(self, scr, path, typ, tform, opts):
        self.leaf = True
        Menu.__init__(self, scr, path, "Choose " + typ)
        self.pagedopts = []
        for opt in opts:
            popt = self.mkopt(None, tform(opt), [self.setchoice(opt), None])
            self.pagedopts.append(popt)
        self.pagedopts.sort(key=lambda x: x['text'])
        self.opts = [
            None,
            self.mkopt('q', "Back", None, hdoc=False)]

    def setchoice(self, opt):
        def f(_): self.option['val'] = opt
        return f
