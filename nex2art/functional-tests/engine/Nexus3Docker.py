import logging
from subprocess import call, check_output

import Nexus3Access
import sys
import time

'''
Spins up Nexus3 instances
'''
class Nexus3Docker:
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def create_new_instance(self, port, dockerport, name, workdir, dockerIP):
        self.log.info("Creating new Nexus3 instance with name " + name)

        if not sys.platform.startswith('darwin') and not sys.platform.startswith('win'):
            self.log.info('Changing permission of Nexus3 work dir')
            code = call(['docker', 'run', '--rm',
            '-v', workdir + ':/nexus-data',
            'busybox', 'sh', '-c', 'chown -R 200 /nexus-data'])

        nexusimage = 'solengha-dockerv2.jfrog.io/soldev/qa/nexus3-test:latest'
        call (['docker', 'pull', nexusimage])

        code = call(['docker', 'run', '--name', name, '-d',
            '-p', port + ":8081",
            '-p', dockerport + ":8082",
            '-v', workdir + ':/nexus-data',
            nexusimage])
        if code != 0:
            return False
        url = 'http://' + dockerIP + ':' + port
        dockerregistry = dockerIP + ':' + dockerport
        nexus = Nexus3Access.Nexus3Access(url, dockerregistry, 'admin', 'admin123', workdir)
        # Wait up to 2 minutes for the instance to come up
        for i in range(0, 12):
            self.log.info('Sleeping for 10 seconds to let Nexus3 startup...')
            time.sleep(10)
            if nexus.get_home():
                return True
            else:
                self.log.info('Nexus3 is still not up.')
        return False

    def delete_instance(self, name, workdir):
        self.log.info('Deleting Nexus3 container with name: ' + name)
        call(['docker', 'stop', name])
        call(['docker', 'rm', name])

        if not sys.platform.startswith('darwin') and not sys.platform.startswith('win'):
            self.log.info('Changing permission of Nexus3 work dir back to current user')
            current_user_id_num = int(check_output(['id', '-u']))
            current_user_id = str(current_user_id_num)
            call(["docker", "run", "--rm", "-v", workdir + ":/nexus-data",
            "busybox", "sh", "-c", "id -u " + current_user_id + " || adduser -u " + current_user_id + " -D host_user; chown -R " + current_user_id + " /nexus-data"])

        call(['rm', '-rf', workdir])
