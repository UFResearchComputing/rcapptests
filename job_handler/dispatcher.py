import config
import os
import time
from loguru import logger 
import subprocess

from job_handler import Test
from job_handler import bash_broilerplate
from job_handler import JobStatus, TestStatus

def submitAllJobs(lmod, yaml_config):
    for module in lmod:
    #    submitJob(lmod, yaml_config, module)
        pass


def submitJob(lmod, yaml_config, module, _moduleVersion = None):
    '''
        Submits slurm jobs for valid modules provided
    '''
    logger.debug(_moduleVersion)

    # Check if valid module name
    if module not in lmod.keys() :
        print("Error: Invalid module '" + module + "'")
        print("Warning: Maybe you have entered '<module>/<version>' with a '-m' flag. Use '-mv' instead.")

        config.RUNNING_TESTS.append(Test(module, "-", "-", time.time(), time.time(), 'N/A', None, JobStatus.INVALID, None, None, TestStatus.MISSING, "-"))
        return

    # Check if valid module/version
    if _moduleVersion is not None :
        moduleVersion = [(module, luaPath) for module in lmod for luaPath in lmod[module] if _moduleVersion == lmod[module][luaPath]['fullName']]
        logger.debug(moduleVersion)
        if len(moduleVersion) == 0 :
            print("Error: Invalid version '" + _moduleVersion + "'")
            print("Warning: Maybe you have entered '<module>' with a '-mv' flag. Use '-m' instead.")

            config.RUNNING_TESTS.append(Test(_moduleVersion, "-", "-", time.time(), time.time(), 'N/A', None, JobStatus.INVALID, None, None, TestStatus.MISSING, "-"))
            return

    logger.debug("Valid module or module/version " + str(_moduleVersion))

    # Parse lmod dict for dependency details
    for luaPath in lmod[module]:
        moduleVersion = lmod[module][luaPath]["fullName"]
        logger.debug(moduleVersion)
        if(_moduleVersion is None or moduleVersion == _moduleVersion):
            testFilePath = os.path.join(config.TEST_PATH, module, "run.sh")

            # Arguments to the sbatch command
            args = []
            dependencies = "-"

            # Check if custom test config (in tests_config.yaml) has been provided and parse it
            if(moduleVersion in yaml_config.keys()):
                testFilePath = yaml_config[moduleVersion]["path"]
                print("Info: Using custom file path " + testFilePath +" for " + moduleVersion)
                if("args" in yaml_config[moduleVersion]):
                    for arg in yaml_config[moduleVersion]["args"].split(' '):
                        args.append(arg)
                    print("Info: Using custom dependency " + str(args) + " for " + moduleVersion)
                    dependencies = "Custom config"

            logger.debug(testFilePath)

            # Add all dependencies to args if not in test config
            if len(args) == 0 and "parentAA" in lmod[module][luaPath]:
                for dependency in lmod[module][luaPath]["parentAA"][0]:
                    if(len(dependencies) == 1):
                        dependencies = dependency
                    else :
                        dependencies += "," + dependency
                    args.append(dependency)
                    
            logger.debug(dependencies)

            # Submit test job
            if(os.path.exists(testFilePath) and os.access(testFilePath, os.R_OK)):
                # Setting trap conditions and module loads in the test files
                newPath = bash_broilerplate.addTrap(testFilePath)

                cmd = ['sbatch', newPath]

                args.append(moduleVersion)
                cmd.extend(args)
                logger.debug(cmd)
                with subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                ) as proc:
                    res_stdout = proc.stdout.read()
                    res_stderr = proc.stderr.read()
                submitTime = time.time()
                logger.debug(res_stdout)
                logger.debug(res_stderr)
                logger.debug("EXIT Code: {}".format(proc.returncode))

                # Add the current job to the RUNNING_TESTS list
                config.RUNNING_TESTS.append(Test(moduleVersion, dependencies, testFilePath, submitTime, None, 'N/A', proc, JobStatus.PENDING, res_stdout, res_stderr, TestStatus.NA, "-"))
            else:
                print("Error: Missing test file /data/apps/tests/" + module + "/run.sh for " + moduleVersion)
                config.RUNNING_TESTS.append(Test(moduleVersion, dependencies, testFilePath, time.time(), None, 'N/A', None, JobStatus.MISSING, None, None, TestStatus.MISSING, "-"))
