import unittest

import engine.DataGenerationFunctions as DataGenerationFunctions
import engine.SharedTestFunctions as SharedTestFunctions

'''
Test the basic functionality of the migration against an actual Artifactory instance
Test the following aspects:
  * Users
  * Groups
  * Permissions
  * LDAP Settings
  * Repositories
  * Artifacts
'''
class Nexus3Test(unittest.TestCase):

    def setUp(self):
        self.nexus = self.__class__.nexus
        self.art = self.__class__.art
        self.packagenum = self.__class__.packagenum
        self.versionsnum = self.__class__.versionsnum
        self.buildnum = self.__class__.buildnum

    def tearDown(self):
        pass

    def test_ldap_test(self):
        conf = self.art.get_configuration().getroot()
        ns = {'art': 'http://artifactory.jfrog.org/xsd/2.1.0'}

        key = conf.find('./art:security/art:ldapSettings/art:ldapSetting/art:key', ns).text
        ldapUrl = conf.find('./art:security/art:ldapSettings/art:ldapSetting/art:ldapUrl', ns).text
        emailAttribute = conf.find('./art:security/art:ldapSettings/art:ldapSetting/art:emailAttribute', ns).text
        searchFilter = conf.find('./art:security/art:ldapSettings/art:ldapSetting/art:search/art:searchFilter', ns).text
        searchBase = conf.find('./art:security/art:ldapSettings/art:ldapSetting/art:search/art:searchBase', ns).text
        groupBaseDn = conf.find('./art:security/art:ldapGroupSettings/art:ldapGroupSetting/art:groupBaseDn', ns).text
        groupNameAttribute = conf.find('./art:security/art:ldapGroupSettings/art:ldapGroupSetting/art:groupNameAttribute', ns).text
        groupMemberAttribute = conf.find('./art:security/art:ldapGroupSettings/art:ldapGroupSetting/art:groupMemberAttribute', ns).text
        groupFilter = conf.find('./art:security/art:ldapGroupSettings/art:ldapGroupSetting/art:filter', ns).text
        enabledLdap = conf.find('./art:security/art:ldapGroupSettings/art:ldapGroupSetting/art:enabledLdap', ns).text

        self.assertEqual('migrated-nexus', key)
        self.assertEqual('ldap://ldap.test.com/dc=jfrog', ldapUrl)
        self.assertEqual('mail', emailAttribute)
        self.assertEqual('(&(objectClass=inetOrgPerson)(uid={0}))', searchFilter)
        self.assertEqual('ou=people', searchBase)
        self.assertEqual('ou=groups', groupBaseDn)
        self.assertEqual('uniqueMember', groupMemberAttribute)
        self.assertEqual('(objectClass=groupOfUniqueNames)', groupFilter)
        self.assertEqual('cn', groupNameAttribute)
        self.assertEqual('migrated-nexus', enabledLdap)
        pass

    def test_users_not_exist(self):
        #do-not-migrate-user
        user = self.art.get_user('do-not-migrate-user')
        self.assertFalse(user)
        pass

    def test_users_exist_test(self):
        # admin
        user = self.art.get_user('admin')
        self.assertTrue(user)
        self.assertTrue(user['admin'])
        self.assertEqual(user['email'], 'admin@example.org')

        # migrate-user
        user = self.art.get_user('migrate-user')
        self.assertTrue(user)
        self.assertTrue(user['admin'])
        self.assertEqual(user['email'], 'migrate@user.com')

        # maven-user
        user = self.art.get_user('maven-user')
        self.assertTrue(user)
        self.assertFalse(user['admin'])
        self.assertEqual(user['email'], 'maven@user.com')
        self.assertTrue('all-maven-snapshot' in user['groups'])

        # disabled-user
        user = self.art.get_user('disabled-user')
        self.assertTrue(user)
        self.assertFalse(user['admin'])
        self.assertEqual(user['email'], 'disabled@user.com')
        pass

    def test_group_migration(self):
        group = self.art.get_group('all-maven-snapshot')
        self.assertTrue(group)
        pass

    def test_permission_migration(self):
        permission = self.art.get_permission('maven-snapshot-edit')
        self.assertTrue(permission)
        self.assertTrue('snapshot-virtual' in permission['repositories'])
        group = permission['principals']['groups']['all-maven-snapshot']
        self.assertTrue(group)
        self.assertTrue(set(['m','d','w','n','r']).issubset(group))
        pass

    def test_generic_migration(self):
        # Validate repositories migration
        repositories = ['generic-local']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'generic')

        # Validate packages migration
        search = self.art.search_artifact('generic-local', '1K')
        self.assertEqual(len(search['results']), self.packagenum * self.versionsnum)
        pass

    def test_maven_release_migration(self):
        # Validate repositories migration
        repositories = ['release-local']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'maven')

        # Validate packages migration
        for package in range(self.packagenum):
            for version in range(self.versionsnum):
                basepackagepath = 'org/test/multi{0}/{1}.0/multi{0}-{1}.0'.format(package + 1, version + 1)
                paths = []
                paths.append(basepackagepath + '.pom')
                paths.append(basepackagepath + '.jar')
                paths.append(basepackagepath + '-sources.jar')
                paths.append(basepackagepath + '-tests.jar')
                for path in paths:
                    self.assertTrue(self.art.artifact_exists('release-local', path))
        pass

    def test_maven_snapshot_migration(self):
        # Validate repositories migration
        repositories = ['snapshot-local', 'maven-remote', 'snapshot-virtual']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'maven')

        # Validate virtual composition
        virtual = self.art.get_repository('snapshot-virtual')
        self.assertEqual(['snapshot-local', 'maven-remote'], virtual['repositories'])

        # Validate packages migration
        for package in range(self.packagenum):
            for version in range(self.versionsnum):
                basepackagesname = 'multi{0}-{1}.1'.format(package + 1, version + 1)
                search = self.art.search_artifact('snapshot-local', basepackagesname)
                self.assertTrue(len(search['results']), 4)
                packagetypes = ['sources.jar', 'tests.jar', '.jar', '.pom']
                packagetypesfound = []
                for result in search['results']:
                    uri = result['uri']
                    if uri.endswith('sources.jar'):
                        packagetypesfound.append('sources.jar')
                    elif uri.endswith('tests.jar'):
                        packagetypesfound.append('tests.jar')
                    elif uri.endswith('.jar'):
                        packagetypesfound.append('.jar')
                    elif uri.endswith('.pom'):
                        packagetypesfound.append('.pom')
                self.assertTrue(set(packagetypes).issubset(packagetypesfound))
        pass

    def test_nuget_migration(self):
        # Validate repositories migration
        repositories = ['nuget-local', 'nuget-remote', 'nuget-virtual']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'nuget')

        # Validate virtual composition
        virtual = self.art.get_repository('nuget-virtual')
        self.assertEqual(['nuget-local', 'nuget-remote'], virtual['repositories'])

        # Validate packages migration
        for package in range(self.packagenum):
            for version in range(self.versionsnum):
                packagepath = 'nuget{0}-{1}-{0}.{1}.{2}.nupkg'.format(package + 1, self.buildnum, version)
                self.assertTrue(self.art.artifact_exists('nuget-virtual', packagepath))
        pass

    def test_npm_migration(self):
        # Validate repositories migration
        repositories = ['npm-local', 'npm-remote', 'npm-virtual']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'npm')

        # Validate virtual composition
        virtual = self.art.get_repository('npm-virtual')
        self.assertEqual(['npm-local', 'npm-remote'], virtual['repositories'])

        # Validate packages migration
        search = self.art.search_artifact('npm-local', 'tgz')
        self.assertEqual(len(search['results']), self.packagenum * self.versionsnum)
        pass

    def test_yum_migration(self):
        # Validate repositories migration
        repositories = ['yum-remote']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'rpm')
        pass

    def test_pypi_migration(self):
        # Validate repositories migration
        repositories = ['pypi-local', 'pypi-remote', 'pypi-virtual']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'pypi')

        # Validate virtual composition
        virtual = self.art.get_repository('pypi-virtual')
        self.assertEqual(['pypi-local', 'pypi-remote'], virtual['repositories'])

        # Validate packages migration
        for package in range(self.packagenum):
            for version in range(self.versionsnum):
                packagepath = 'packages/pypi{0}-{1}/{0}.1.{2}/pypi{0}-{1}-{0}.1.{2}.tar.gz'.format(package + 1, self.buildnum, version)
                self.assertTrue(self.art.artifact_exists('pypi-virtual', packagepath))
        pass

    def test_docker_migration(self):
        # Validate repositories migration
        repositories = ['docker-local', 'docker-remote', 'docker-virtual']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'docker')

        # Validate virtual composition
        virtual = self.art.get_repository('docker-virtual')
        self.assertEqual(['docker-local', 'docker-remote'], virtual['repositories'])

        # Validate packages migration
        for package in range(self.packagenum):
            for version in range(self.versionsnum):
                tagpath = 'test/image{0}-{1}/1.{2}/'.format(package + 1, self.buildnum, version)

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

    def test_gems_migration(self):
        # Validate repositories migration
        repositories = ['gems-local', 'gems-remote', 'gems-virtual']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'gems')

        # Validate virtual composition
        virtual = self.art.get_repository('gems-virtual')
        self.assertEqual(['gems-local', 'gems-remote'], virtual['repositories'])

        # Validate packages migration
        for majversion in [1, 2]:
            for minversion in [1, 2]:
                packagepath = 'gems/mygem-{0}.{1}.0.gem'.format(majversion, minversion)
                self.assertTrue(self.art.artifact_exists('gems-virtual', packagepath))
        pass

    def test_gitlfs_migration(self):
        # Validate repository migration
        repodata = self.art.get_repository('gitlfs-local')
        self.assertTrue(repodata)
        self.assertEqual(repodata['packageType'], 'gitlfs')

        # Validate packages migration
        sha2s = []
        sha2s.append("5d6bc26962c3fbac969275acf9d0b83524e00068249bb9e5b14e34e2d6e7b103")
        sha2s.append("1020ea9a02876097a6d8b8998304eaba608eec5b3e3904d25c9fc29e624e08fe")
        sha2s.append("c022cfb0491c88e8c566eb08926385eb8c95009bfa6083b009bfbaaea743ec3a")
        sha2s.append("cf2d34a0fabeed6f3a5d682ab1babd6cf484aebcdfd1bd5fd2b4fc0b74ac1aae")
        for package in sha2s:
            packagepath = 'objects/{0}/{1}/{2}'.format(package[0:2], package[2:4], package)
            self.assertTrue(self.art.artifact_exists('gitlfs-local', packagepath))
        pass

    @classmethod
    def setUpClass(cls):
        SharedTestFunctions.start_logging()
        cls.group = SharedTestFunctions.create_group_identifier()
        cls.nexus_name, cls.nexus = SharedTestFunctions.create_nexus3_instance(cls.group)
        cls.art_name, cls.art = SharedTestFunctions.create_art_instance(cls.group)

        # Configure package generation
        cls.packagenum = 2
        cls.versionsnum = 2
        cls.buildnum = 1

        # Create generic packages
        DataGenerationFunctions.generate_generic_packages(
            cls.packagenum * cls.versionsnum,
            cls.nexus.workdir + '/generated_data/generic',
            cls.nexus.url + '/repository/generic-local',
            cls.nexus.username, cls.nexus.password
        )

        # Create maven release packages
        DataGenerationFunctions.generate_maven_release_packages(
            cls.packagenum, cls.versionsnum, 'org.test',
            cls.nexus.workdir + '/generated_data/maven_release',
            cls.nexus.url + '/repository/release-local',
            cls.nexus.username, cls.nexus.password
        )

        # Create maven snapshot packages
        DataGenerationFunctions.generate_maven_snapshot_packages(
            cls.packagenum, cls.versionsnum, 'org.test',
            cls.nexus.workdir + '/generated_data/maven_snapshot',
            cls.nexus.url + '/repository/snapshot-local',
            cls.nexus.username, cls.nexus.password
        )

        # Create nuget packages
        DataGenerationFunctions.generate_nuget_packages('nuget',
            cls.packagenum, cls.versionsnum, cls.buildnum,
            cls.nexus.url + '/repository/nuget-local/',
            'b3ba6c0f-4a0a-3411-b5a9-7d0da7128ea3')

        # Create NPM packages
        DataGenerationFunctions.generate_npm_packages(cls.packagenum,
            cls.versionsnum, cls.nexus.url + '/repository/npm-remote/',
            cls.nexus.url + '/repository/npm-local/',
            cls.nexus.username, cls.nexus.password)

        # Create pypi packages
        DataGenerationFunctions.generate_pypi_packages('pypi', cls.packagenum, cls.versionsnum,
            cls.buildnum, 'egg', cls.nexus.url + '/repository/pypi-local/',
            cls.nexus.username, cls.nexus.password)

        # Create docker packages
        DataGenerationFunctions.generate_docker_packages('image', 'test', cls.packagenum,
            cls.versionsnum, 2, cls.buildnum, 'busybox',
            cls.nexus.dockerregistry,
            cls.nexus.username, cls.nexus.password)

        # Execute migration
        SharedTestFunctions.perform_migration('nexus3MigrationConfig.json',
            cls.nexus, cls.art)

    @classmethod
    def tearDownClass(cls):
        SharedTestFunctions.delete_art_instance(cls.art_name)
        SharedTestFunctions.delete_nexus3_instance(cls.nexus_name, cls.nexus.workdir)

if __name__ == '__main__':
    unittest.main()
