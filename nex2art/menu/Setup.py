import base64
import urllib2
import urlparse
from ..core import Menu

class Setup(Menu):
    def __init__(self, scr):
        Menu.__init__(self, scr, "Initial Setup")
        self.urlopt = self.mkopt('a', "Artifactory URL", '|', verif=self.churl)
        self.useropt = self.mkopt('u', "Artifactory Username", '|',
                                  verif=self.chuser)
        self.paswopt = self.mkopt('p', "Artifactory Password", '*',
                                  verif=self.chpasw)
        self.opts = [
            self.mkopt('n', "Nexus Path", '|', verif=self.chpath),
            self.urlopt,
            self.useropt,
            self.paswopt,
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Back", None, hdoc=False)]

    def chpath(self, newpath):
        status = self.scr.nexus.refresh(newpath)
        if status == True: return True
        self.scr.msg = ('err', status)
        return False

    def churl(self, _):
        self.pingserver()
        return self.urlopt['stat']

    def chuser(self, _):
        self.pingserver()
        return self.useropt['stat']

    def chpasw(self, _):
        self.pingserver()
        return self.paswopt['stat']

    def pingserver(self):
        url = list(urlparse.urlparse(str(self.urlopt['val'])))
        user, pasw = self.useropt['val'], self.paswopt['val']
        if url[0] not in ('http', 'https'): url = None
        elif len(url[2]) == 0 or url[2][-1] != '/': url[2] += '/'
        headers, conn, stat = {'User-Agent': 'nex2art'}, None, None
        if user != None and pasw != None:
            enc = base64.b64encode(user + ':' + pasw)
            headers['Authorization'] = "Basic " + enc
        if url != None:
            path = url[2] + 'api/system/ping'
            nurl = urlparse.urlunsplit((url[0], url[1], path, '', ''))
            try:
                req = urllib2.Request(nurl, None, headers)
                resp = urllib2.urlopen(req)
                stat = resp.getcode()
            except urllib2.HTTPError as ex: stat = ex.code
            except urllib2.URLError as ex: stat = ex.reason
        self.urlopt['stat'] = self.urlopt['val'] == None
        self.useropt['stat'] = self.useropt['val'] == None
        self.paswopt['stat'] = self.paswopt['val'] == None
        if stat in (200, 401):
            self.urlopt['stat'] = True
            self.scr.artifactory.url = url
        else: self.scr.artifactory.url = None
        if user != None and pasw != None and stat == 200:
            self.useropt['stat'] = True
            self.paswopt['stat'] = True
            self.scr.artifactory.user = user
            self.scr.artifactory.pasw = pasw
        else:
            self.scr.artifactory.user = None
            self.scr.artifactory.pasw = None
        if stat == 401 or (user != pasw and (user == None or pasw == None)):
            self.scr.msg = ('err', "Incorrect username and/or password.")
        elif stat != 200:
            self.scr.msg = ('err', "Unable to access Artifactory instance.")
