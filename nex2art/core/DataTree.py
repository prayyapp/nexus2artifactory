class DataTree(object):
    def __init__(self, scr, data):
        self.scr = scr
        self.save = True
        self.valid = True
        self._data = data
        if isinstance(data, dict):
            self._data = {}
            for k, v in data.items():
                self._data[k] = DataTree(self.scr, v)
        elif isinstance(data, list):
            self._data = []
            for v in data:
                self._data.append(DataTree(self.scr, v))

    def _getdata(self):
        self.prune()
        if not isinstance(self._data, (dict, list)): return self._data
        raise TypeError("Unable to provide internal subtree object")

    def _setdata(self, data):
        if not isinstance(data, (dict, list)):
            self._data = data
            return
        data = DataTree(self.scr, data)
        data.prune()
        self._data = data._data

    data = property(_getdata, _setdata)

    def __eq__(self, other):
        if not isinstance(other, DataTree): return False
        this = self.todict()
        that = other.todict()
        self.scr.format.trim(this)
        self.scr.format.trim(that)
        return this == that

    def __ne__(self, other):
        return not (self == other)

    def __getitem__(self, keys):
        if not hasattr(type(keys), '__iter__'): keys = [keys]
        if len(keys) == 0: return self
        if not isinstance(self._data, dict):
            clsname = self._data.__class__.__name__
            msg = "Referenced '" + clsname + "' object cannot be indexed at '"
            msg += str(keys[0]) + "'"
            raise TypeError(msg)
        if keys[0] not in self._data:
            self._data[keys[0]] = DataTree(self.scr, {})
        return self._data[keys[0]][keys[1:]]

    def init(self, val):
        if self._data == {} or self._data == [] or self._data == None:
            self.data = val

    def values(self):
        if self._data == {}: self._data = []
        if not isinstance(self._data, list):
            raise TypeError("Unable to provide values")
        return self._data

    def items(self):
        if not isinstance(self._data, dict):
            raise TypeError("Unable to provide items")
        return self._data.items()

    def isleaf(self):
        return not isinstance(self._data, (dict, list))

    def islist(self):
        return isinstance(self._data, list)

    def prune(self):
        if isinstance(self._data, list):
            for v in self._data: v.prune()
        elif isinstance(self._data, dict):
            for k, v in self._data.items():
                v.prune()
                if v._data == {}: del self._data[k]

    def clone(self):
        data = self._data
        if isinstance(self._data, list):
            data = []
            for v in self._data: data.append(v.clone())
        elif isinstance(self._data, dict):
            data = {}
            for k, v in self._data.items(): data[k] = v.clone()
        clone = DataTree(self.scr, None)
        clone._data = data
        clone.save = self.save
        clone.valid = self.valid
        return clone

    def todict(self):
        if isinstance(self._data, list):
            data = []
            for v in self._data:
                if v.save: data.append(v.todict())
            return sorted(data)
        if isinstance(self._data, dict):
            data = {}
            for k, v in self._data.items():
                if v.save: data[k] = v.todict()
            return data
        return self._data
