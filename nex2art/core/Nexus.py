import os
from . import Nexus2, Nexus3

class EmptyAttributes(object):
    def __init__(self):
        pass

    def __getattr__(self, name):
        return None

class Nexus(object):
    def __init__(self, scr):
        self.scr = scr
        self.nexusversion = 0
        self._nex2 = Nexus2(self.scr)
        self._nex3 = Nexus3(self.scr)
        self._empty = EmptyAttributes()
        self.vpath = True
        self.vurl = True
        self.vuser = True
        self.vpasw = True

    def __getattr__(self, name):
        if self.nexusversion == 2: return getattr(self._nex2, name)
        if self.nexusversion == 3: return getattr(self._nex3, name)
        if name in ('security', 'ldap'): return self._empty
        if name == 'repos': return None
        raise AttributeError

    def checkNexus(self):
        self.nexusversion = 0
        path = self.scr.state["Initial Setup"]["Nexus Data Directory"].data
        if path == None:
            self.vpath = "No Nexus path provided"
            self.vurl, self.vuser, self.vpasw = True, True, True
            self.scr.format.update()
            return
        path = os.path.abspath(path)
        etc = os.path.join(path, 'etc')
        conf = os.path.join(path, 'conf')
        blobs = os.path.join(path, 'blobs')
        storage = os.path.join(path, 'storage')
        if os.path.isdir(etc) and os.path.isdir(blobs):
            self.nexusversion = 3
            self._nex3.checkNexus()
        elif os.path.isdir(conf) and os.path.isdir(storage):
            self.nexusversion = 2
            self._nex2.checkNexus()
        else:
            self.scr.log.error("Nexus config and store directories do not exist.")
            self.vpath = "Given path is not a valid Nexus instance."
            self.vurl, self.vuser, self.vpasw = True, True, True
            self.scr.format.update()
