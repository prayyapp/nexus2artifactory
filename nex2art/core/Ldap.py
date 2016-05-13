import os
import xml.etree.ElementTree as ET

class Ldap:
    def __init__(self):
        self.initialize()

    def initialize(self):
        self.ldap = None

    def refresh(self, path):
        ldapxml = os.path.join(path, 'conf', 'ldap.xml')
        if os.path.isfile(ldapxml):
            try: self.ldap = self.getldap(ldapxml)
            except: pass

    def getldap(self, ldapxml):
        tmpdata, ldap = {}, {}
        for prop in ET.parse(ldapxml).getroot().iter():
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
