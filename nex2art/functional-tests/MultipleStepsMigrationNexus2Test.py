import unittest
from multiprocessing import Process
import engine.DataGenerationFunctions as DataGenerationFunctions
import engine.SharedTestFunctions as SharedTestFunctions


'''
Test multiple steps data migration for Nexus 2
'''
class MultipleStepsMigrationNexus2Test(unittest.TestCase):

    def setUp(self):
        self.nexus = self.__class__.nexus
        self.art = self.__class__.art
        self.packagenum = 10
        self.versionsnum = 2

    def tearDown(self):
        pass

    def runmigration(self):
        SharedTestFunctions.perform_migration('nexus2MigrationConfig.json',
            self.nexus, self.art)

    def uploadpackages(self, buildnumber):
        DataGenerationFunctions.generate_maven_release_packages(
            self.packagenum, self.versionsnum, 'org.test.build' + str(buildnumber),
            self.nexus.workdir + '/generated_data/maven_release_build' + str(buildnumber),
            self.nexus.url + '/content/repositories/release-local',
            self.nexus.username, self.nexus.password
        )

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
                    basepackagepath = 'org/test/build{2}/multi{0}/{1}.0/multi{0}-{1}.0'.format(package + 1, version + 1, build + 1)
                    paths = []
                    paths.append(basepackagepath + '.pom')
                    paths.append(basepackagepath + '.jar')
                    paths.append(basepackagepath + '-sources.jar')
                    paths.append(basepackagepath + '-tests.jar')
                    for path in paths:
                        self.assertTrue(self.art.artifact_exists('release-local', path))
        pass

    @classmethod
    def setUpClass(cls):
        SharedTestFunctions.start_logging()
        cls.group = SharedTestFunctions.create_group_identifier()
        cls.nexus_name, cls.nexus = SharedTestFunctions.create_nexus2_instance(cls.group)
        cls.art_name, cls.art = SharedTestFunctions.create_art_instance(cls.group)

    @classmethod
    def tearDownClass(cls):
        SharedTestFunctions.delete_art_instance(cls.art_name)
        SharedTestFunctions.delete_nexus2_instance(cls.nexus_name, cls.nexus.workdir)

if __name__ == '__main__':
    unittest.main()
