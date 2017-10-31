import os
import base64
import hashlib
import logging
import xml.etree.ElementTree as ET

class Ldap(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.initialize()

    def initialize(self):
        self.ldap = None

    def refresh(self, path):
        ldapxml = os.path.join(path, 'conf', 'ldap.xml')
        self.log.info("Reading LDAP config from %s.", ldapxml)
        if os.path.isfile(ldapxml):
            try:
                self.ldap = self.getldap(ldapxml)
                self.log.info("Successfully read LDAP config.")
            except:
                self.log.exception("Error reading LDAP config:")
        else: self.log.info("LDAP config file does not exist, skipping.")

    def decodePassword(self, pasw):
        bs = base64.b64decode(pasw)
        digest = hashlib.sha1()
        digest.update(chr(1)*64 + bs[1:9]*8 + '\0C\0M\0M\0D\0w\0o\0V\0\0'*4)
        accum = digest.digest()
        for _ in xrange(22):
            digest = hashlib.sha1()
            digest.update(accum)
            accum = digest.digest()
        j, out = 0, []
        S = range(256)
        for i in xrange(256):
            j = (j + S[i] + ord(accum[i % 16])) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        for char in bs[9:]:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))
        return ''.join(out)

    def getldap(self, ldapxml):
        tmpdata, ldap = {}, {}
        root = ET.parse(ldapxml).getroot()
        itr = None
        try: itr = root.iter()
        except AttributeError: itr = root.getiterator()
        for prop in itr:
            tmpdata[prop.tag] = prop.text
        proto, host = tmpdata['protocol'], tmpdata['host']
        port, base = tmpdata['port'], tmpdata['searchBase']
        url = proto + '://' + host
        if (proto, port) not in (('ldap', '389'), ('ldaps', '636')):
            url += ':' + port
        url += '/' + base
        ldap['ldapUrl'] = url
        uoc = tmpdata['userObjectClass']
        uid = tmpdata['userIdAttribute']
        filt = '(&(objectClass=' + uoc + ')(' + uid + '={0})'
        if 'ldapFilter' in tmpdata and len(tmpdata['ldapFilter']) > 0:
            ufilt = tmpdata['ldapFilter']
            if ufilt[0] != '(' or ufilt[-1] != ')':
                ufilt = '(' + ufilt + ')'
            filt += ufilt
        filt += ')'
        ldap['searchFilter'] = filt
        ldap['emailAttribute'] = tmpdata['emailAddressAttribute']
        if 'systemUsername' in tmpdata:
            ldap['managerDn'] = tmpdata['systemUsername']
        if 'systemPassword' in tmpdata:
            try:
                manpass = self.decodePassword(tmpdata['systemPassword'])
                ldap['managerPassword'] = manpass
            except: pass
        if 'userBaseDn' in tmpdata:
            ldap['searchBase'] = tmpdata['userBaseDn']
        if 'userSubtree' in tmpdata:
            ldap['searchSubTree'] = tmpdata['userSubtree']
        else: ldap['searchSubTree'] = 'false'
        lgar = 'ldapGroupsAsRoles'
        if lgar in tmpdata and tmpdata[lgar] == 'true':
            gma = 'groupMemberAttribute'
            umoa = 'userMemberOfAttribute'
            goc = 'group'
            if umoa in tmpdata:
                ldap[gma] = tmpdata[umoa]
                ldap['strategy'] = 'DYNAMIC'
                ldap['groupNameAttribute'] = 'cn'
            else:
                ldap[gma] = tmpdata[gma]
                ldap['strategy'] = 'STATIC'
                ldap['groupNameAttribute'] = tmpdata['groupIdAttribute']
                goc = tmpdata['groupObjectClass']
            ldap['filter'] = '(objectClass=' + goc + ')'
            if 'groupBaseDn' in tmpdata:
                ldap['groupBaseDn'] = tmpdata['groupBaseDn']
            if 'groupSubtree' in tmpdata:
                ldap['subTree'] = tmpdata['groupSubtree']
            else: ldap['subTree'] = 'false'
        return ldap
