class Option(object):
    def __init__(self, scr, vals, path, realpath, isbranch):
        self.scr = scr
        self.vals = vals
        self.path = path
        self.realpath = realpath
        state = self.scr.state[self.realpath]
        if state.save == True: state.save = isbranch or self.vals['save']
        if not isbranch and self['val'] == None: self['val'] = self.vals['val']

    def __getitem__(self, key):
        if key != 'val' and key != 'stat':
            return self.vals[key]
        v = self.scr.state[self.path if key == 'val' else self.realpath]
        if key == 'stat': return v.valid
        elif v.isleaf(): return v.data
        elif v.islist(): return v.todict()
        else: return None

    def __setitem__(self, key, item):
        if key != 'val' and key != 'stat':
            self.vals[key] = item
            return
        v = self.scr.state[self.path if key == 'val' else self.realpath]
        if key == 'stat': v.valid = item
        else: v.data = item
