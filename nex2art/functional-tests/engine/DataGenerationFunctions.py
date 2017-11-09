import ConfigParser
import os, sys
import logging
from subprocess import call

def get_docker_host_hostname():
    hostname = '172.17.0.1'
    if sys.platform.startswith('darwin'):
        return 'docker.for.mac.localhost'
    if sys.platform.startswith('win'):
        return '10.0.75.1'
    return hostname

def fix_docker_host_hostname(url):
    return url.replace('localhost', get_docker_host_hostname())

# Generate maven release packages
def generate_maven_release_packages(numpackages, numversions, groupid, tempfolder, urltopush, username, password):
    logging.info('Generating ' + str(numpackages) + ' * ' + str(numversions) + ' maven release packages...')

    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/maven-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm',
        '-e', 'skip_artifactory=true',
        '-e', 'NUM_UNIQUE_FILE_PER_SIZE=0',
        '-e', 'UNIQUE_FILE_PER_SIZE=1k',
        '-e', 'group_id=' + groupid,
        '-v', tempfolder + ':/data',
        generatorimage,
        str(numpackages), str(numversions), '0', 'release'])

    for root, subfolders, files in os.walk(tempfolder):
        for filename in files:
            filepath = os.path.join(root, filename)
            uploadpath = filepath.replace(tempfolder, '')
            uploadurl = urltopush + uploadpath
            logging.info("Pushing artifact to " + uploadurl)
            call(['curl', '-u', username + ':' + password,
                '--upload-file', filepath, uploadurl])

# Generate maven snapshot packages
def generate_maven_snapshot_packages(numpackages, numversions, groupid, tempfolder, urltopush, username, password):
    logging.info('Generating ' + str(numpackages) + ' * ' + str(numversions) + ' maven snapshot packages...')
    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/maven-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm',
        '-e', 'skip_artifactory=true',
        '-e', 'NUM_UNIQUE_FILE_PER_SIZE=0',
        '-e', 'UNIQUE_FILE_PER_SIZE=1k',
        '-e', 'group_id=' + groupid,
        '-v', tempfolder + ':/data',
        generatorimage,
        str(numpackages), str(numversions), '1', 'snapshot', '1'])

    for root, subfolders, files in os.walk(tempfolder):
        for filename in files:
            for version in range(numversions):
                filepath = os.path.join(root, filename)
                uploadpath = filepath.replace(tempfolder, '')
                uploadurl = urltopush + uploadpath
                logging.info("Pushing artifact to " + uploadurl)
                call(['curl', '-u', username + ':' + password,
                    '--upload-file', filepath, uploadurl])

# Generate generic packages
def generate_generic_packages(numpackages, tempfolder, urltopush, username, password):
    logging.info('Generating ' + str(numpackages) + ' generic packages...')
    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/generic-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm',
        '-e', 'FNUM=' + str(numpackages),
        '-e', 'skip_artifactory=true',
        '-v', tempfolder + ':/data/stress',
        generatorimage])

    for filename in os.listdir(tempfolder):
        url = urltopush + '/' + filename + '.txt'
        logging.info("Pushing artifact to " + url)
        call(['curl', '-u', username + ':' + password,
        '--upload-file', tempfolder + '/' + filename, url])

# Generate Nuget packages
def generate_nuget_packages(name, numpackages, numversions, buildnumber, repo, apikey):
    logging.info('Generating ' + str(numpackages) + ' * ' + str(numversions) + ' Nuget packages...')
    fixed_repo = fix_docker_host_hostname(repo)
    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/nuget-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm',
        '-e', 'NAME=' + name,
        '-e', 'PNUM=' + str(numpackages),
        '-e', 'FNUM=1',
        '-e', 'BUILD_NUMBER=' + str(buildnumber),
        '-e', 'NUMOFVERSIONS=' + str(numversions),
        '-e', 'COMMAND=gd',
        '-e', 'NUGET_SOURCE=' + fixed_repo,
        '-e', 'APIKEY=' + apikey,
        generatorimage])

# Generate NPM packages
def generate_npm_packages(numpackages, numversions, reporesolve, repopublish, username, password):
    logging.info('Generating ' + str(numpackages) + ' * ' + str(numversions) + ' NPM packages...')
    fixed_reporesolve = fix_docker_host_hostname(reporesolve)
    fixed_repopublish = fix_docker_host_hostname(repopublish)
    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/npm-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm',
        '-e', 'USER_NAME=' + username,
        '-e', 'PASSWORD=' + password,
        '-e', 'PNUM=' + str(numpackages),
        '-e', 'VNUM=' + str(numversions),
        '-e', 'REGISTRY_RESOLVE=' + fixed_reporesolve,
        '-e', 'REGISTRY_PUBLISH=' + fixed_repopublish,
        generatorimage])

# Generate yum packages
def generate_yum_packages(name, numpackages, buildnumber, tempfolder, urltopush, username, password):
    logging.info('Generating ' + str(numpackages) + ' yum packages...')
    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/rpm-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm',
        '-e', 'NAME=' + name,
        '-e', 'PNUM=' + str(numpackages),
        '-e', 'FNUM=1',
        '-e', 'BUILD_NUMBER=' + str(buildnumber),
        '-e', 'COMMAND=g',
        '-v', tempfolder + ':/data/output',
        generatorimage])

    for filename in os.listdir(tempfolder):
        url = urltopush + '/' + filename
        logging.info("Pushing artifact to " + url)
        call(['curl', '-u', username + ':' + password,
        '--upload-file', tempfolder + '/' + filename, url])

# Generate pypi packages
def generate_pypi_packages(name, numpackages, numversions, buildnumber, disttype, repositoryurl, username, password):
    logging.info('Generating ' + str(numpackages) + ' * ' + str(numversions) + ' pypi packages...')
    fixed_repositoryurl = fix_docker_host_hostname(repositoryurl)
    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/pypi-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm',
        '-e', 'NAME=' + name,
        '-e', 'PNUM=' + str(numpackages),
        '-e', 'FNUM=1',
        '-e', 'NUMOFVERSIONS=' + str(numversions),
        '-e', 'DIST=' + disttype,
        '-e', 'BUILD_NUMBER=' + str(buildnumber),
        '-e', 'COMMAND=gd',
        '-e', 'REPOSITORY_URL=' + fixed_repositoryurl,
        '-e', 'ARTIUSER=' + username,
        '-e', 'PASSWORD=' + password,
        generatorimage])

# Generate docker packages
def generate_docker_packages(name, namespace, numpackages, numversions, numlayers,
                                buildnumber, baseimage, registry, username, password):
    logging.info('Generating ' + str(numpackages) + ' * ' + str(numversions) + ' docker images...')
    fixed_registry = fix_docker_host_hostname(registry)
    generatorimage = 'solengha-dockerv2.jfrog.io/soldev/qa/docker-generator:generic'
    call (['docker', 'pull', generatorimage])
    call(['docker', 'run', '--rm', '--privileged',
        '-e', 'DNAME=' + name,
        '-e', 'NAMESPACE=' + namespace,
        '-e', 'INUM=' + str(numpackages),
        '-e', 'NUMOFTAGS=' + str(numversions),
        '-e', 'LNUM=' + str(numlayers),
        '-e', 'FNUM=1',
        '-e', 'BUILD_NUMBER=' + str(buildnumber),
        '-e', 'MODE=bp',
        '-e', 'baseImage=' + baseimage,
        '-e', 'DOCKER_REGISTRY=' + fixed_registry,
        '-e', 'ARTIUSER=' + username,
        '-e', 'PASSWORD=' + password,
        generatorimage])
