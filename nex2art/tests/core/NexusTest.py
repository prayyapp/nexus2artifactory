import unittest
import os, sys
# Allows easily running the tests without setting up python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from nex2art.core import Nexus

class NexusTest(unittest.TestCase):
    def setUp(self):
        self.nexus = Nexus()
        self.resourcesDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'NexusTest')

    def tearDown(self):
        self.nexus = None

    def test_getYumCapabilities(self):
        self.assertEqual(self.nexus.getYumCapabilities(
            os.path.join(self.resourcesDir, 'nonexistent.xml')), [])
        self.assertEqual(self.nexus.getYumCapabilities(
            os.path.join(self.resourcesDir, 'noYumRepoCapabilities.xml')), [])
        self.assertEqual(self.nexus.getYumCapabilities(
            os.path.join(self.resourcesDir, 'localYumRepoCapabilities.xml')), ['releases'])
        self.assertEqual(sorted(self.nexus.getYumCapabilities(
            os.path.join(self.resourcesDir, 'multipleYumRepoCapabilities.xml'))),
            sorted(['public', 'releases', 'central']))

    def test_getRepoClass(self):
        # TODO: Implement
        pass

    def test_getPackType(self):
        # TODO: Implement
        pass

if __name__ == '__main__':
    unittest.main()