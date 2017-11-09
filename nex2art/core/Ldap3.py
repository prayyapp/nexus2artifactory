import logging

class Ldap3(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.initialize()

    def initialize(self):
        self.ldap = None

    def refresh(self, data):
        self.log.info("Reading LDAP config from Nexus.")
        ldaps = {}
        for ldap in data['ldaps']: ldaps[ldap['name']] = self.getldap(ldap)
        self.ldap = ldaps
        self.log.info("Successfully read LDAP config.")

    def getldap(self, data):
        ldap = {'nexusName': data['name']}
        url = data['protocol'] + '://' + data['hostName']
        if (data['protocol'], data['port']) not in (('ldap', 389), ('ldaps', 636)):
            url += ':' + str(data['port'])
        url += '/' + data['searchBase']
        ldap['ldapUrl'] = url
        filt = '(&(objectClass=' + data['userObjectClass'] + ')('
        filt += data['userIdAttribute'] + '={0})'
        if data['ldapFilter'] != None and len(data['ldapFilter']) > 0:
            ufilt = data['ldapFilter']
            if ufilt[0] != '(' or ufilt[-1] != ')':
                ufilt = '(' + ufilt + ')'
            filt += ufilt
        filt += ')'
        ldap['searchFilter'] = filt
        ldap['emailAttribute'] = data['emailAddressAttribute']
        if data['systemUsername'] != None and len(data['systemUsername']) > 0:
            ldap['managerDn'] = data['systemUsername']
        if data['systemPassword'] != None and len(data['systemPassword']) > 0:
            ldap['managerPassword'] = data['systemPassword']
        if data['userBaseDn'] != None and len(data['userBaseDn']) > 0:
            ldap['searchBase'] = data['userBaseDn']
        ldap['searchSubTree'] = 'true' if data['userSubtree'] else 'false'
        if data['ldapGroupsAsRoles']:
            goc = 'group'
            umoa = data['userMemberOfAttribute']
            if umoa != None and len(umoa) > 0:
                ldap['groupMemberAttribute'] = data['userMemberOfAttribute']
                ldap['strategy'] = 'DYNAMIC'
                ldap['groupNameAttribute'] = 'cn'
            else:
                ldap['groupMemberAttribute'] = data['groupMemberAttribute']
                ldap['strategy'] = 'STATIC'
                ldap['groupNameAttribute'] = data['groupIdAttribute']
                goc = data['groupObjectClass']
            ldap['filter'] = '(objectClass=' + goc + ')'
            if data['groupBaseDn'] != None and len(data['groupBaseDn']) > 0:
                ldap['groupBaseDn'] = data['groupBaseDn']
            ldap['subTree'] = 'true' if data['groupSubtree'] else 'false'
        return ldap
