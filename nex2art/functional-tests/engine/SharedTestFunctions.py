import ConfigParser
import json
import logging
import os
import random
import tempfile

import ArtifactoryAccess
import ArtifactoryDocker
import Nexus2Access
import Nexus2Docker
import Nexus3Access
import Nexus3Docker
import sys

# Allows easily running the tests without setting up python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from nex2art.core import Setup, Screen, Progress, Password


def start_logging():
    level = logging.INFO
    fmt = "%(asctime)s [%(threadName)s] [%(levelname)s]"
    fmt += " (%(name)s:%(lineno)d) - %(message)s"
    formatter = logging.Formatter(fmt)
    logger = logging.getLogger()
    if not len(logger.handlers):
        logger.setLevel(level)
        stdouth = logging.StreamHandler(sys.stdout)
        stdouth.setFormatter(formatter)
        logger.addHandler(stdouth)
    msg = "\n\nNexus To Artifactory Migration Tool - Functional Tests\n\n"
    logger.info('\n' + '='*60 + msg + '='*60 + '\n')

# Create docker container group identifier
def create_group_identifier():
    return str(random.randint(1,10000))

# Creates an Artifactory docker container based on the config settings.ini
# Returns the name of the container and the access to it
def create_art_instance(group):
    # Read and verify the config file
    config = ConfigParser.ConfigParser()
    config.read(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/config/settings.ini')
    if not config.has_section('Artifactory'):
        sys.exit('Missing settings.ini file or Artifactory section')
    if not config.has_option('Artifactory', 'version'):
        sys.exit('Missing version from settings.ini')
    if not config.has_option('Artifactory', 'exposedPort'):
        sys.exit('Missing exposedPort from settings.ini')
    # Extract contents from config and setup URL
    version = config.get('Artifactory', 'version')
    host = 'localhost'
    port = config.get('Artifactory', 'exposedPort')
    url = 'http://' + host + ':' + port + '/artifactory'
    # Create a semi-random name for the container
    container_name = 'nex2art_test_art_' + group
    try:
        with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/config/artifactory.lic', 'r') as myfile:
            license_contents=myfile.read()
    except IOError as ex:
        sys.exit('Unable to read license from config/artifactory.lic')
    # Start a new Artifactory instance and set up a connection to it
    docker = ArtifactoryDocker.ArtifactoryDocker()
    if not docker.create_new_instance(version, port, container_name, host, license_contents):
        sys.exit('Failed to create the Artifactory instance')
    return container_name, ArtifactoryAccess.ArtifactoryAccess(url, 'admin', 'password')

# Deletes a container by name
def delete_art_instance(container_name):
    docker = ArtifactoryDocker.ArtifactoryDocker()
    docker.delete_instance(container_name)

# Performs an import from the nexus_conf_dir into the Artifactory referenced by art_access
# The nexus_conf_dir must have: migrationConfig.json and the nexus data/conf directory
def perform_migration(migration_config_file, nexus_access, art_access):
    tempConfigFilePath = create_migration_config_temp_file(migration_config_file, nexus_access, art_access)
    setup = Setup(['-n', '-q', '-f', tempConfigFilePath])
    try:
        scr = Screen(None, setup.args)
        prog = Progress(scr)
        logging.info("Attempting to run migration.")
        if scr.loadst != True:
            logging.warning("Unable to run migration: %s", str(scr.loadst))
            return
        if scr.state.valid != True:
            logging.warning("Unable to run migration, errors found.")
            return
        status = prog.show(scr.state.todict())
        if status == True: logging.info("Migration successfully run.")
        else:
            logging.warning("Error running migration: %s.", status)
            return
    except BaseException as ex:
        if not isinstance(ex, SystemExit):
            logging.exception("Error running Nexus migration tool:")
        raise

# Creates a temporary copy of <nexus_conf_dir>/resources/migrationConfig.json
# replacing the Initial Setup information with the actual data for the test
# execution
def create_migration_config_temp_file(migration_config_file, nexus_access, art_access):
    try:
        with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/resources/' + migration_config_file, 'r') as migrationConfigFile:
            config = json.load(migrationConfigFile)

            # Set environment information
            config['Initial Setup']['Nexus Data Directory'] = nexus_access.workdir
            if isinstance(nexus_access, Nexus3Access.Nexus3Access):
                config['Initial Setup']['Nexus URL'] = nexus_access.url
                config['Initial Setup']['Nexus Username'] = nexus_access.username
                config['Initial Setup']['Nexus Password'] = Password.encrypt(nexus_access.password)
            config['Initial Setup']['Artifactory URL'] = art_access.url
            config['Initial Setup']['Artifactory Username'] = art_access.username
            config['Initial Setup']['Artifactory Password'] = Password.encrypt(art_access.password)

            # Save configuration to temporary file
            fd, path = tempfile.mkstemp()
            print("Temporary configuration file will be created at: " + path)
            with open(path, 'w') as tmpFile:
                json.dump(config, tmpFile)

            return path

    except IOError as ex:
        print('Unable to read migration config file from resources/' + migration_config_file)
        return

# Creates an Nexus2 docker container based on the config settings.ini
# Returns the name of the container and the access to it
def create_nexus2_instance(group):
    # Read and verify the config file
    config = ConfigParser.ConfigParser()
    config.read(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/config/settings.ini')
    if not config.has_section('Nexus2'):
        sys.exit('Missing settings.ini file or Nexus2 section')
    if not config.has_option('Nexus2', 'exposedPort'):
        sys.exit('Missing exposedPort from settings.ini')
    if not config.has_section('General'):
        sys.exit('Missing settings.ini file or General section')
    if not config.has_option('General', 'tempFolder'):
        sys.exit('Missing tempFolder from settings.ini')
    # Extract contents from config and setup URL
    host = 'localhost'
    port = config.get('Nexus2', 'exposedPort')
    tempFolder = config.get('General', 'tempFolder')
    url = 'http://' + host + ':' + port + '/nexus'
    # Create a semi-random name for the container
    container_name = 'nex2art_test_nexus2_' + group
    workdir = tempFolder + '/' + container_name
    logging.info('Nexus2 workdir will be: ' + workdir)
    # Start a new Nexus2 instance and set up a connection to it
    docker = Nexus2Docker.Nexus2Docker()
    if not docker.create_new_instance(port, container_name, workdir, host):
        sys.exit('Failed to create the Nexus2 instance')
    return container_name, Nexus2Access.Nexus2Access(url, 'admin', 'admin123', workdir)

# Deletes a container by name
def delete_nexus2_instance(container_name, workdir):
    docker = Nexus2Docker.Nexus2Docker()
    docker.delete_instance(container_name, workdir)

# Creates an Nexus3 docker container based on the config settings.ini
# Returns the name of the container and the access to it
def create_nexus3_instance(group):
    # Read and verify the config file
    config = ConfigParser.ConfigParser()
    config.read(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/config/settings.ini')
    if not config.has_section('Nexus3'):
        sys.exit('Missing settings.ini file or Nexus3 section')
    if not config.has_option('Nexus3', 'exposedPort'):
        sys.exit('Missing exposedPort from settings.ini')
    if not config.has_option('Nexus3', 'dockerRegistryPort'):
        sys.exit('Missing dockerRegistryPort from settings.ini')
    if not config.has_section('General'):
        sys.exit('Missing settings.ini file or General section')
    if not config.has_option('General', 'tempFolder'):
        sys.exit('Missing tempFolder from settings.ini')
    # Extract contents from config and setup URL
    host = 'localhost'
    port = config.get('Nexus3', 'exposedPort')
    dockerport = config.get('Nexus3', 'dockerRegistryPort')
    tempFolder = config.get('General', 'tempFolder')
    url = 'http://' + host + ':' + port
    dockerregistry = host + ':' + dockerport
    # Create a semi-random name for the container
    container_name = 'nex2art_test_nexus3_' + group
    workdir = tempFolder + '/' + container_name
    logging.info('Nexus3 workdir will be: ' + workdir)
    # Start a new Nexus3 instance and set up a connection to it
    docker = Nexus3Docker.Nexus3Docker()
    if not docker.create_new_instance(port, dockerport, container_name, workdir, host):
        sys.exit('Failed to create the Nexus3 instance')
    return container_name, Nexus3Access.Nexus3Access(url, dockerregistry, 'admin', 'admin123', workdir)

# Deletes a container by name
def delete_nexus3_instance(container_name, workdir):
    docker = Nexus3Docker.Nexus3Docker()
    docker.delete_instance(container_name, workdir)
