import unittest
from multiprocessing import Process
import engine.DataGenerationFunctions as DataGenerationFunctions
import engine.SharedTestFunctions as SharedTestFunctions


'''
Test multiple steps data migration for Nexus 3
'''
class MultipleStepsMigrationNexus3Test(unittest.TestCase):

    def setUp(self):
        self.nexus = self.__class__.nexus
        self.art = self.__class__.art
        self.packagenum = 10
        self.versionsnum = 2

    def tearDown(self):
        pass

    def runmigration(self):
        SharedTestFunctions.perform_migration('nexus3MigrationConfig.json',
            self.nexus, self.art)

    def uploadpackages(self, buildnumber):
        DataGenerationFunctions.generate_docker_packages('image', 'test', self.packagenum,
            self.versionsnum, 2, buildnumber, 'busybox',
            self.nexus.dockerregistry,
            self.nexus.username, self.nexus.password)

    def test_multiple_steps_migration(self):
        # Upload some packages
        self.uploadpackages(1)

        # Execute migration and upload more packages in paralell
        migrationprocess = Process(target=self.runmigration)
        uploadprocess = Process(target=self.uploadpackages, args=(2,))
        migrationprocess.start()
        uploadprocess.start()
        migrationprocess.join()
        uploadprocess.join()

        # Execute final migration
        self.runmigration()

        # Validate migrated data
        for build in range(2):
            for package in range(self.packagenum):
                for version in range(self.versionsnum):
                    tagpath = 'test/image{0}-{1}/1.{2}/'.format(package + 1, build + 1, version)

                    # Validate manifest file
                    manifestpath = tagpath + 'manifest.json'
                    manifest = self.art.get_artifact_json_content('docker-virtual', manifestpath)
                    self.assertTrue(manifest)

                    # Validate layers
                    layers = []
                    layers.append(manifest['config']['digest'])
                    for layer in manifest['layers']:
                        layers.append(layer['digest'])
                    for layer in layers:
                        layerpath = tagpath + layer.replace(':', '__')
                        self.assertTrue(self.art.artifact_exists('docker-virtual', layerpath))
        pass

    @classmethod
    def setUpClass(cls):
        SharedTestFunctions.start_logging()
        cls.group = SharedTestFunctions.create_group_identifier()
        cls.nexus_name, cls.nexus = SharedTestFunctions.create_nexus3_instance(cls.group)
        cls.art_name, cls.art = SharedTestFunctions.create_art_instance(cls.group)

    @classmethod
    def tearDownClass(cls):
        SharedTestFunctions.delete_art_instance(cls.art_name)
        SharedTestFunctions.delete_nexus3_instance(cls.nexus_name, cls.nexus.workdir)

if __name__ == '__main__':
    unittest.main()
