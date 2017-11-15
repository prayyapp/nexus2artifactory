import unittest
import os, sys
import xml.etree.ElementTree as ET
# Allows easily running the tests without setting up python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from nex2art.core import Security

class NexusTest(unittest.TestCase):
    def setUp(self):
        self.security = Security()
        self.resourcesDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'SecurityTest')

    def tearDown(self):
        self.security = None

    def test_getTargets(self):
        xml = ET.parse(os.path.join(self.resourcesDir, 'simpleRepoTargets.xml'))
        self.security.gettargets(xml)
        targs = self.security.targs
        self.assertIsNotNone(targs)
        self.assertEqual(len(targs), 10)

    def test_getUsers(self):
        with open(os.path.join(self.resourcesDir, 'defaultRoleMap.txt'), 'r') as roleFile:
            self.security.allroles = eval(roleFile.read())
        # Admin + anon only
        xml = ET.parse(os.path.join(self.resourcesDir, 'basicUsers.xml'))
        self.security.getusers(xml)
        users = self.security.users
        self.assertEqual(len(users), 2)
        self.assertEqual(sorted(users), sorted(('admin', 'anonymous')))
        self.assertEqual(users['admin']['email'], 'bar@yourcompany.com')
        self.assertEqual(users['anonymous']['email'], 'foo@yourcompany.com')

    def test_getRoles(self):
        with open(os.path.join(self.resourcesDir, 'defaultPrivMap.txt'), 'r') as privFile:
            self.security.allprivmap = eval(privFile.read())
        xml = ET.parse(os.path.join(self.resourcesDir, 'basicUsers.xml'))
        self.security.getroles(xml)
        roles = self.security.roles
        self.assertEqual(len(roles), 1)
        self.assertIsNotNone(roles['test-role'])


    def test_getPrivileges(self):
        with open(os.path.join(self.resourcesDir, 'defaultTargetMap.txt'), 'r') as targetFile:
            self.security.targs = eval(targetFile.read())
        xml = ET.parse(os.path.join(self.resourcesDir, 'basicUsers.xml'))
        self.security.getprivileges(xml)
        privs = self.security.privs
        self.assertEqual(len(privs), 1)
        self.assertIsNotNone(privs['test-permission-priv'])
        self.assertEqual(privs['test-permission-priv']['repo'], 'paco1')

if __name__ == '__main__':
    unittest.main()