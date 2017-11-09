import logging
from subprocess import call, check_output

import sys
import time

import Nexus2Access

'''
Spins up Nexus2 instances
'''
class Nexus2Docker:
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def create_new_instance(self, port, name, workdir, dockerIP):
        self.log.info("Creating new Nexus2 instance with name " + name)

        if not sys.platform.startswith('darwin') and not sys.platform.startswith('win'):
            self.log.info('Changing permission of Nexus2 work dir')
            code = call(['docker', 'run', '--rm',
            '-v', workdir + ':/sonatype-work',
            'busybox', 'sh', '-c', 'chown -R 200 /sonatype-work'])

        nexusimage = 'solengha-dockerv2.jfrog.io/soldev/qa/nexus2-test:latest'
        call (['docker', 'pull', nexusimage])

        code = call(['docker', 'run', '--name', name, '-d', '-p', port + ":8081",
            '-v', workdir + ':/sonatype-work',
            nexusimage])
        if code != 0:
            return False
        url = 'http://' + dockerIP + ':' + port + '/nexus'
        nexus = Nexus2Access.Nexus2Access(url, 'admin', 'admin123', workdir)
        # Wait up to 2 minutes for the instance to come up
        for i in range(0, 12):
            self.log.info('Sleeping for 10 seconds to let Nexus2 startup...')
            time.sleep(10)
            if nexus.get_home():
                return True
            else:
                self.log.info('Nexus2 is still not up.')
        return False

    def delete_instance(self, name, workdir):
        self.log.info('Deleting Nexus2 container with name: ' + name)
        call(['docker', 'stop', name])
        call(['docker', 'rm', name])

        if not sys.platform.startswith('darwin') and not sys.platform.startswith('win'):
            self.log.info('Changing permission of Nexus2 work dir back to current user')
            current_user_id_num = int(check_output(['id', '-u']))
            current_user_id = str(current_user_id_num)
            call(["docker", "run", "--rm", "-v", workdir + ":/sonatype-work",
            "busybox", "sh", "-c", "id -u " + current_user_id + " || adduser -u " + current_user_id + " -D host_user; chown -R " + current_user_id + " /sonatype-work"])

        call(['rm', '-rf', workdir])
