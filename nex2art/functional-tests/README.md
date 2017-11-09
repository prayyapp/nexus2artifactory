# Nexus2Artifactory Integration Test

## Requirements
* A valid Artifactory pro license
* Docker 1.10+

# Running the tests
* Add a valid `artifactory.lic` to the config dir
* Copy the `settings.ini.example` in the config to `settings.ini` and configure it as desired
  * version - The version of the Artifactory instance to use for testing (4.4.2+)
  * exposedPort - The port to expose on the container (typically 8081 unless there is a conflict)
  * dockerIP - The IP address that containers are accessed from (normally localhost)
* From the command line, run:  
```
cd nex2art/functionl-tests
python -m  unittest discover -v -p "*Test.py"
```
