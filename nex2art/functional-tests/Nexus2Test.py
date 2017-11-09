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
class Nexus2Test(unittest.TestCase):

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
        self.assertEqual(user['email'], 'changeme@yourcompany.com')

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

        # deployment
        user = self.art.get_user('deployment')
        self.assertTrue(user)
        self.assertFalse(user['admin'])
        self.assertEqual(user['email'], 'changeme1@yourcompany.com')
        pass

    def test_group_migration(self):
        group = self.art.get_group('all-maven-snapshot')
        self.assertTrue(group)
        pass

    def test_permission_migration(self):
        permission = self.art.get_permission('maven-snapshot')
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
                nugetid = 'nuget{0}-{1}'.format(package + 1, self.buildnum)
                packagepath = 'nuget{0}-{1}/{0}.{1}.{2}/nuget{0}-{1}-{0}.{1}.{2}.nupkg'.format(package + 1, self.buildnum, version)
                self.assertTrue(self.art.artifact_exists('nuget-virtual', packagepath))
                properties = self.art.get_artifact_properties('nuget-virtual', packagepath)
                self.assertEqual(nugetid, properties['properties']['nuget.id'][0])
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
        repositories = ['yum-local', 'yum-remote', 'yum-virtual']
        for repository in repositories:
            repodata = self.art.get_repository(repository)
            self.assertTrue(repodata)
            self.assertEqual(repodata['packageType'], 'rpm')

        # Validate virtual composition
        virtual = self.art.get_repository('yum-virtual')
        self.assertEqual(['yum-local', 'yum-remote'], virtual['repositories'])

        # Validate packages migration
        for package in range(self.packagenum * self.versionsnum):
            packagename = 'yum{0}_{1}'.format(package + 1, self.buildnum)
            packagepath = 'yum{0}_{2}-{0}-{1}.x86_64.rpm'.format(package + 1, package + 2, self.buildnum)
            self.assertTrue(self.art.artifact_exists('yum-virtual', packagepath))
            properties = self.art.get_artifact_properties('yum-virtual', packagepath)
            self.assertEqual(packagename, properties['properties']['rpm.metadata.name'][0])
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

    @classmethod
    def setUpClass(cls):
        SharedTestFunctions.start_logging()
        cls.group = SharedTestFunctions.create_group_identifier()
        cls.nexus_name, cls.nexus = SharedTestFunctions.create_nexus2_instance(cls.group)
        cls.art_name, cls.art = SharedTestFunctions.create_art_instance(cls.group)

        # Configure package generation
        cls.packagenum = 2
        cls.versionsnum = 2
        cls.buildnum = 1

        # Create generic packages
        DataGenerationFunctions.generate_generic_packages(
            cls.packagenum * cls.versionsnum,
            cls.nexus.workdir + '/generated_data/generic',
            cls.nexus.url + '/content/repositories/generic-local',
            cls.nexus.username, cls.nexus.password
        )

        # Create maven release packages
        DataGenerationFunctions.generate_maven_release_packages(
            cls.packagenum, cls.versionsnum, 'org.test',
            cls.nexus.workdir + '/generated_data/maven_release',
            cls.nexus.url + '/content/repositories/release-local',
            cls.nexus.username, cls.nexus.password
        )

        # Create maven snapshot packages
        DataGenerationFunctions.generate_maven_snapshot_packages(
            cls.packagenum, cls.versionsnum, 'org.test',
            cls.nexus.workdir + '/generated_data/maven_snapshot',
            cls.nexus.url + '/content/repositories/snapshot-local',
            cls.nexus.username, cls.nexus.password
        )

        # Create nuget packages
        DataGenerationFunctions.generate_nuget_packages('nuget',
            cls.packagenum, cls.versionsnum, cls.buildnum,
            cls.nexus.url + '/service/local/nuget/nuget-local/',
            '0e9e2e69-2f8a-3191-8df4-e0bac4a50670')

        # Create NPM packages
        DataGenerationFunctions.generate_npm_packages(cls.packagenum,
            cls.versionsnum, cls.nexus.url + '/content/repositories/npm-remote/',
            cls.nexus.url + '/content/repositories/npm-local/',
            cls.nexus.username, cls.nexus.password)

        # Create yum packages
        DataGenerationFunctions.generate_yum_packages('yum', cls.packagenum * cls.versionsnum,
            cls.buildnum, cls.nexus.workdir + '/generated_data/yum',
            cls.nexus.url + '/content/repositories/yum-local/',
            cls.nexus.username, cls.nexus.password)

        # Execute migration
        SharedTestFunctions.perform_migration('nexus2MigrationConfig.json',
            cls.nexus, cls.art)

    @classmethod
    def tearDownClass(cls):
        SharedTestFunctions.delete_art_instance(cls.art_name)
        SharedTestFunctions.delete_nexus2_instance(cls.nexus_name, cls.nexus.workdir)

if __name__ == '__main__':
    unittest.main()
