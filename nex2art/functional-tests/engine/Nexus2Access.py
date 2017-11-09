import logging

from HTTPAccess import HTTPAccess

'''
 An API for accessing Nexus

 The API is for testing and not for general usage. As such, functionality such as uploading/downloading is not
 implemented.
'''

class Nexus2Access(HTTPAccess):
    def __init__(self, url, username, password, workdir, ignore_cert = False, exlog=False):
        super(Nexus2Access, self).__init__( url, username, password, ignore_cert, exlog)
        self.log = logging.getLogger(__name__)
        self.workdir = workdir

    def get_home(self):
        return self.get_call_wrapper('/')