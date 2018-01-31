import sys
import ssl
import logging
import argparse
from functools import wraps

# Windows seems to have an issue with writing some logs to curses window if
# there are no handlers specified. This handler does nothing, but it prevents
# that issue.
class NilHandler(logging.Handler):
    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None

class Setup(object):
    def __init__(self, argssource):
        self.argssource = argssource
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
        noninteractive = args.non_interactive and not args.silent
        if logfile == None and not noninteractive:
            logging.getLogger().addHandler(NilHandler())
            return
        level = logging.INFO
        if args.log_level == 'error': level = logging.ERROR
        elif args.log_level == 'warning': level = logging.WARNING
        elif args.log_level == 'debug': level = logging.DEBUG
        fmt = "%(asctime)s [%(threadName)s] [%(levelname)s]"
        fmt += " (%(name)s:%(lineno)d) - %(message)s"
        formatter = logging.Formatter(fmt)
        logger = logging.getLogger()
        logger.setLevel(level)
        if logfile != None:
            fileh = logging.FileHandler(logfile)
            fileh.setFormatter(formatter)
            logger.addHandler(fileh)
        if noninteractive:
            stdouth = logging.StreamHandler(sys.stdout)
            stdouth.setFormatter(formatter)
            logger.addHandler(stdouth)
        msg = "\n\nNexus To Artifactory Migration Tool\n\n"
        logger.info('\n' + '='*60 + msg + '='*60 + '\n')

    def getargs(self):
        help = [
            "Migrate Sonatype Nexus instances to JFrog Artifactory.",
            "the file to use for logging (default: don't write logs)",
            "the threshold to use for the logging level, if logs are written",
            "whether to disable ssl verification (e.g. for self-signed certs)",
            "the configuration file to load automatically on start",
            "migrate immediately without displaying the UI (requires -f)",
            "Turn off logs output for non interactive mode"]
        chcs = 'error', 'warning', 'info', 'debug'
        parser = argparse.ArgumentParser(description=help[0])
        parser.add_argument('-l', '--log-file', help=help[1])
        parser.add_argument('-q', '--silent',
                            action='store_true', help=help[6])
        parser.add_argument('-v', '--log-level', choices=chcs, help=help[2])
        parser.add_argument('-s', '--ssl-no-verify',
                            action='store_true', help=help[3])
        parser.add_argument('-f', '--load-file', help=help[4])
        parser.add_argument('-n', '--non-interactive',
                            action='store_true', help=help[5])
        args = parser.parse_args(self.argssource)
        if args.load_file == None and args.non_interactive:
            parser.error("option --load-file is required for non-interactive mode")
        return args
