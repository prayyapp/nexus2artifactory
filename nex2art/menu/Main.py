import json
import copy
import logging
from ..core import Menu, Progress
from . import Setup, Repo, Security, Options, Safety

# The main menu. This is the first menu that appears when the tool is started,
# and it's the hub that everything else can be accessed through. It contains
# special options for saving and loading a configuration to and from a file,
# running verification on an entire configuration at any time, and running a
# full migration based on the current configuration.
class Main(Menu):
    # Initialize the main menu by setting up the options.
    def __init__(self, scr):
        Menu.__init__(self, scr, "Nexus -> Artifactory")
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing Main Menu.")
        self.scr.mainmenu = self
        self.saveopt = self.mkopt('s', "Save Configuration",
                                  ['|', self.save], save=False)
        self.loadopt = self.mkopt('l', "Load Configuration",
                                  [self.preload, '|', self.load], save=False)
        self.repopt = self.mkopt('r', "Repository Migration Setup", Repo(scr))
        self.secopt = self.mkopt('u', "Security Migration Setup", Security(scr))
        self.optopt = self.mkopt('o', "Options Migration Setup", Options(scr))
        self.opts = [
            self.mkopt('i', "Initial Setup", [Setup(scr), self.statrefresh]),
            self.repopt,
            self.secopt,
            self.optopt,
            None,
            self.saveopt,
            self.loadopt,
            self.mkopt('v', "Verify Configuration", self.doverify),
            self.mkopt('x', "Run Migration", self.runmigration),
            None,
            self.mkopt('h', "Help", '?'),
            self.mkopt('q', "Exit", None, hdoc=False)]
        self.verify()
        self.scr.msg = None
        self.scr.oldstate = self.collectconf()
        self.log.debug("Main Menu initialized.")

    # When setup runs, refresh the view, as there may be new statuses.
    def statrefresh(self, _):
        self.repopt['stat'] = self.repopt['act'][0].verify()
        self.secopt['stat'] = self.secopt['act'][0].verify()
        self.optopt['stat'] = self.optopt['act'][0].verify()
        self.scr.msg = None

    # Run full verification on the configuration, using the menu's verify()
    # function. Print the result.
    def doverify(self, _):
        self.log.info("Verifying current state.")
        if self.verify():
            self.log.info("Current state verified successfully.")
            self.scr.msg = ('val', "Configuration verified successfully.")
        else:
            self.log.warning("Current state verified, errors found.")
            self.scr.msg = ('err', "Configuration verified, errors found.")

    # Run the actual migration, and print the result.
    def runmigration(self, _):
        self.log.info("Attempting to run migration.")
        if not self.verify():
            self.log.warning("Unable to run migration, errors found.")
            self.scr.msg = ('err', "Cannot run migration, errors found.")
            return
        status = Progress(self.scr).show(self.collectconf())
        if status == True:
            self.log.info("Migration successfully run.")
            self.scr.msg = ('val', "Migration successful!")
        else:
            self.log.warning("Error running migration: %s.", status)
            self.scr.msg = ('err', "Migration error: " + status)

    # Serialize the current configuration state as a JSON object, and save it to
    # a file. The parameter 'sel' is the menu option that ran this function.
    def save(self, sel):
        if sel['val'] == None: return
        self.log.info("Saving configuration to file %s.", sel['val'])
        self.verify()
        f = None
        try:
            f = open(sel['val'], 'w')
            conf = self.collectconf()
            json.dump(conf, f, indent=4)
            self.log.info("Configuration saved successfully.")
            self.scr.msg = ('val', "Successfully saved to specified file.")
            self.scr.oldstate = conf
            sel['stat'] = True
        except:
            self.log.exception("Error saving configuration:")
            self.scr.msg = ('err', "Unable to save to specified file.")
            sel['stat'] = False
        finally:
            if f != None: f.close()
        if sel['stat'] == True and self.loadopt['val'] == None:
            self.loadopt['val'] = sel['val']

    # Before loading a JSON object from a file, if there are unsaved changes,
    # ensure that the user wants to discard them.
    def preload(self, sel):
        if self.scr.modified() and not Safety(self.scr).show(): return False

    # Load a JSON object from a file, and apply the configuration state
    # specified by that object as the current state. The parameter 'sel' is the
    # menu option that ran this function.
    def load(self, sel):
        if sel['val'] == None: return
        self.log.info("Loading configuration from file %s.", sel['val'])
        f = None
        try:
            f = open(sel['val'], 'r')
            conf = json.load(f)
            self.applyconf(copy.deepcopy(conf))
            if self.verify():
                self.log.info("Configuration loaded successfully.")
                self.scr.msg = ('val', "Configuration loaded successfully.")
            else:
                self.log.warning("Configuration loaded, errors found.")
                self.scr.msg = ('err', "Configuration loaded, errors found.")
            self.scr.oldstate = conf
            sel['stat'] = True
        except:
            self.log.exception("Error loading configuration:")
            self.scr.msg = ('err', "Unable to load from specified file.")
            sel['stat'] = False
        finally:
            if f != None: f.close()
        if sel['stat'] == True and self.saveopt['val'] == None:
            self.saveopt['val'] = sel['val']
