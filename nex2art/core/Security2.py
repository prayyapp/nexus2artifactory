import os
import re
import logging
import xml.etree.ElementTree as ET
from . import getBuiltinTargs, getBuiltinPrivs, getBuiltinPrivmap, getBuiltinRoles

class Security2(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.initialize()

    def initialize(self):
        self.users = None
        self.roles = None
        self.privs = None
        self.privmap = None

    def refresh(self, path, usertargs, repos):
        path = os.path.abspath(path)
        config = os.path.join(path, 'conf', 'security.xml')
        self.log.info("Reading security config from %s.", config)
        if not os.path.isfile(config):
            self.log.error("Security config file does not exist.")
            return "Given path is not a valid Nexus instance."
        try:
            xml = ET.parse(config).getroot()
            targs = getBuiltinTargs()
            targs.update(usertargs)
            privs = getBuiltinPrivs(targs)
            privmap = getBuiltinPrivmap(privs)
            privmap.update(self.buildviewprivs(repos))
            nprivs, nprivmap = self.getprivileges(xml, targs)
            privs.update(nprivs)
            privmap.update(nprivmap)
            self.flattentargets(privs)
            roles = getBuiltinRoles(privmap)
            roles.update(self.getroles(xml, privmap))
            for role in roles.values():
                self.flattenrole(role, roles)
                self.consolidateprivs(role)
            users = self.getusers(xml, roles)
            self.log.info("Successfully read security config.")
            self.users = users
            self.roles = roles
            self.privs = privs
            self.privmap = privmap
            return True
        except:
            self.log.exception("Error reading security config:")
            return "Configuration file security.xml is not valid."

    def gettargets(self, xml):
        targets = {}
        targsxml = xml.find('repositoryTargets')
        if targsxml == None: return {}
        for targetxml in targsxml.findall('repositoryTarget'):
            target = {'patterns': [], 'defincpat': [], 'defexcpat': []}
            target['name'] = targetxml.find('id').text
            target['ptype'] = targetxml.find('contentClass').text
            xmlpatterns = targetxml.find('patterns')
            if xmlpatterns == None: xmlpatterns = []
            else: xmlpatterns = xmlpatterns.findall('pattern')
            for patxml in xmlpatterns:
                pattern = patxml.text
                target['patterns'].append(pattern)
                if pattern == ".*":
                    target['defincpat'].append("**")
                elif pattern == ".*maven-metadata\\.xml.*":
                    target['defincpat'].append("**/*maven-metadata.xml*")
                elif pattern == "(?!.*-sources.*).*":
                    target['defexcpat'].append("**/*-sources.*/**")
                else:
                    target['defincpat'] = False
                    target['defexcpat'] = False
                    break
            targets[target['name']] = target
        return targets

    def flattentargets(self, privs):
        for priv in privs.values():
            targ = priv['target']
            priv['ptype'] = targ['ptype']
            priv['patterns'] = targ['patterns']
            priv['defincpat'] = targ['defincpat']
            priv['defexcpat'] = targ['defexcpat']
            del priv['target']

    def getusers(self, xml, roles):
        users = {}
        xmlusers = xml.find('users')
        if xmlusers == None: return {}
        for userxml in xmlusers.findall('user'):
            user = {'builtin': False}
            user['username'] = userxml.find('id').text
            user['email'] = userxml.find('email').text
            user['enabled'] = userxml.find('status').text == 'active'
            users[user['username']] = user
        urmxml = xml.find('userRoleMappings')
        if urmxml == None: return {}
        for mapxml in urmxml.findall('userRoleMapping'):
            user = {'email': None, 'enabled': True, 'builtin': False}
            user['username'] = mapxml.find('userId').text
            if user['username'] in users: user = users[user['username']]
            user['realm'] = mapxml.find('source').text.lower()
            if user['realm'] == 'default': user['realm'] = 'internal'
            user['roles'] = []
            xmlroles = mapxml.find('roles')
            if xmlroles == None: xmlroles = []
            else: xmlroles = xmlroles.findall('role')
            for rolexml in xmlroles:
                if rolexml.text in roles:
                    user['roles'].append(roles[rolexml.text])
            users[user['username']] = user
        return users

    def flattenrole(self, role, roles):
        while len(role['roles']) > 0:
            child = role['roles'].pop()
            if child not in roles: continue
            privs = self.flattenrole(roles[child], roles)
            if roles[child]['admin']: role['admin'] = True
            for priv in privs:
                if priv not in role['privileges']:
                    role['privileges'].append(priv)
        return role['privileges']

    def consolidateprivs(self, role):
        privs, privmap, consprivs = {}, {}, []
        for privref in role['privileges']:
            if privref['type'] == 'loosetarget':
                privname = privref['priv']['name']
                if privname in privs and privname in privmap:
                    privs[privname].append(privref['method'])
                else:
                    privs[privname] = [privref['method']]
                    privmap[privname] = privref['priv']
            else: consprivs.append(privref)
        for privname, methods in privs.items():
            priv = privmap[privname]
            methodstr = ''
            if len(methods) > 0: methodstr += 'r'
            if 'create' in methods or 'update' in methods: methodstr += 'w'
            if 'delete' in methods or 'update' in methods: methodstr += 'd'
            if 'w' in methodstr: methodstr += 'n'
            if 'w' in methodstr: methodstr += 'm'
            if len(methodstr) <= 0: methodstr = None
            dct = {
                'id': priv['name'],
                'type': 'target',
                'priv': priv,
                'method': methodstr,
                'needadmin': False
            }
            consprivs.append(dct)
        role['privileges'] = consprivs

    def buildviewprivs(self, repos):
        privs = {}
        for repo in repos:
            priv = {}
            priv['id'] = 'repository-' + repo['id']
            priv['repo'] = repo['id']
            priv['type'] = 'view'
            priv['needadmin'] = False
            privs[priv['id']] = priv
        return privs

    def getroles(self, xml, privmap):
        roles = {}
        xmlroles = xml.find('roles')
        if xmlroles == None: return {}
        for rolexml in xmlroles.findall('role'):
            role = {'privileges': [], 'roles': [], 'admin': False, 'builtin': False}
            role['groupName'] = rolexml.find('id').text
            if rolexml.find('description') != None:
                role['description'] = rolexml.find('description').text
            else: role['description'] = ''
            xmlprivileges = rolexml.find('privileges')
            if xmlprivileges != None:
                for privxml in xmlprivileges.findall('privilege'):
                    if privxml.text in privmap:
                        role['privileges'].append(privmap[privxml.text])
            xmlprivroles = rolexml.find('roles')
            if xmlprivroles != None:
                for srolexml in xmlprivroles.findall('role'):
                    role['roles'].append(srolexml.text)
            roles[role['groupName']] = role
        return roles

    def getprivileges(self, xml, targs):
        privs, privmap = {}, {}
        xmlprivileges = xml.find('privileges')
        if xmlprivileges == None: return {}, {}
        for privxml in xmlprivileges.findall('privilege'):
            priv, privtmp, privref = None, {}, {}
            xmlproperties = privxml.find('properties')
            if xmlproperties == None: xmlproperties = []
            else: xmlproperties = xmlproperties.findall('property')
            for propxml in xmlproperties:
                privtmp[propxml.find('key').text] = propxml.find('value').text
            name, method = privxml.find('name').text, privtmp['method']
            mthdstrs = method.split(',')
            if len(mthdstrs) == 2 and mthdstrs[1] == 'read':
                method = mthdstrs[0]
            matcher = re.match('^(.+) - \\(' + method + '\\)$', name)
            if matcher != None: name = matcher.group(1)
            if name in privs: priv = privs[name]
            else:
                priv = {'name': name, 'builtin': False}
                if privtmp['repositoryTargetId'] in targs:
                    priv['target'] = targs[privtmp['repositoryTargetId']]
                if (privtmp['repositoryId'] != None
                    and len(privtmp['repositoryId'].strip()) > 0):
                    priv['repo'] = privtmp['repositoryId']
                elif (privtmp['repositoryGroupId'] != None
                      and len(privtmp['repositoryGroupId'].strip()) > 0):
                    priv['repo'] = privtmp['repositoryGroupId']
                else: priv['repo'] = "*"
                privs[name] = priv
            privref['id'] = privxml.find('id').text
            privref['method'] = method
            privref['type'] = 'loosetarget'
            privref['priv'] = priv
            privref['needadmin'] = False
            privmap[privref['id']] = privref
        return privs, privmap
