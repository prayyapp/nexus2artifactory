import unittest
import os, sys
import xml.etree.ElementTree as ET
# Allows easily running the tests without setting up python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from nex2art.core import Security2

class Security2Test(unittest.TestCase):
    def setUp(self):
        self.security = Security2()
        self.resourcesDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'Security2Test')

    def tearDown(self):
        self.security = None

    def test_getTargets(self):
        xml = ET.parse(os.path.join(self.resourcesDir, 'simpleRepoTargets.xml'))
        targs = self.security.gettargets(xml)
        self.assertIsNotNone(targs)
        self.assertEqual(len(targs), 10)

    def test_getUsers(self):
        with open(os.path.join(self.resourcesDir, 'defaultRoleMap.txt'), 'r') as roleFile:
            roles = eval(roleFile.read())
        # Admin only
        xml = ET.parse(os.path.join(self.resourcesDir, 'basicUsers.xml'))
        users = self.security.getusers(xml, roles)
        self.assertEqual(len(users), 1)
        self.assertEqual(sorted(users), ['admin'])
        self.assertEqual(users['admin']['email'], 'bar@yourcompany.com')

    def test_getRoles(self):
        with open(os.path.join(self.resourcesDir, 'defaultPrivMap.txt'), 'r') as privFile:
            privmap = eval(privFile.read())
        xml = ET.parse(os.path.join(self.resourcesDir, 'basicUsers.xml'))
        roles = self.security.getroles(xml, privmap)
        self.assertEqual(len(roles), 1)
        self.assertIsNotNone(roles['test-role'])

    def test_getPrivileges(self):
        with open(os.path.join(self.resourcesDir, 'defaultTargetMap.txt'), 'r') as targetFile:
            targs = eval(targetFile.read())
        xml = ET.parse(os.path.join(self.resourcesDir, 'basicUsers.xml'))
        privs, privmap = self.security.getprivileges(xml, targs)
        self.assertEqual(len(privs), 1)
        self.assertIsNotNone(privs['test-permission-priv'])
        self.assertEqual(privs['test-permission-priv']['repo'], 'paco1')

if __name__ == '__main__':
    unittest.main()
