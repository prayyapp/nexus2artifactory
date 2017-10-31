import ssl
import logging
import argparse
from functools import wraps

class Setup(object):
    def __init__(self):
        self.fixssl()
        self.args = self.getargs()
        self.startlogging(self.args)

    # Some versions of SSL have a bug that causes an exception to be thrown when
    # a connection is made using TLSv1.1/TLSv1.2. This hack works around this
    # problem by forcing TLSv1.0.
    def fixssl(self):
        def sslwrap(func):
            @wraps(func)
            def bar(*args, **kw):
                kw['ssl_version'] = ssl.PROTOCOL_TLSv1
                return func(*args, **kw)
            return bar
        ssl.wrap_socket = sslwrap(ssl.wrap_socket)

    def startlogging(self, args):
        logfile = args.log_file
        if logfile == None: return
        level = logging.INFO
        if args.log_level == 'error': level = logging.ERROR
        elif args.log_level == 'warning': level = logging.WARNING
        elif args.log_level == 'debug': level = logging.DEBUG
        with open(logfile, 'a') as f:
            f.write('='*60 + "\n\n")
            f.write("Nexus To Artifactory Migration Tool\n\n")
            f.write('='*60 + "\n\n")
        fmt = "%(asctime)s [%(threadName)s] [%(levelname)s]"
        fmt += " (%(name)s:%(lineno)d) - %(message)s"
        logging.basicConfig(format=fmt, filename=logfile, level=level)

    def getargs(self):
        help = [
            "Migrate Sonatype Nexus instances to JFrog Artifactory.",
            "the file to use for logging (default: don't write logs)",
            "the threshold to use for the logging level, if logs are written",
            "whether to disable ssl verification (e.g. for self-signed certs)"]
        chcs = 'error', 'warning', 'info', 'debug'
        parser = argparse.ArgumentParser(description=help[0])
        parser.add_argument('-l', '--log-file', help=help[1])
        parser.add_argument('-v', '--log-level', choices=chcs, help=help[2])
        parser.add_argument('-s', '--ssl-no-verify',
                            action='store_true', help=help[3])
        return parser.parse_args()
