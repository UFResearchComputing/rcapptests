"""
    This script will run tests on specified modules and provides a report
    Author: Sohaib Uddin Syed (sohaibuddinsyed@ufl.edu), June 2023 - Present
"""

import argparse
import sys
import os
import subprocess
import time
import threading
import logging
import json
import yaml
from loguru import logger
import config
import output
import subprocess
import shlex
import json
import os 


JobStatus = config.JobStatus
TestStatus = config.TestStatus

testStatus = {}

class Test(object):
    def __init__(self, module, dependencies, filepath, startTime, endTime,  jobId, proc, jobStatus, jobOut, jobErr, testStatus, exitCode):
        self.module = module
        self.dependencies = dependencies
        self.filepath = filepath
        self.startTime = startTime
        self.endTime = endTime
        self.jobId = jobId
        self.proc = proc
        self.jobStatus = jobStatus
        self.jobOut = jobOut
        self.jobErr = jobErr
        self.testStatus = testStatus
        self.exitCode = exitCode

def parse_args(print_help=False):
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write("error: %s\n" % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        usage="apptests [options] [group]",
        description="""
        
        Internal tool to run application tests.

        How to test an application:
        1) Copy sample test script from /data/apps/test/apptests/run.sh into
        /data/apps/test/<app> where 'app' is the application to be tested.
        2) Modify the test script as needed.
        3) Run the tests. (Eg: apptests -m <app>, apptests -mv app/version etc)
        4) Check the report and slurm_logs in /data/apps/test/apptests/, full
        paths will be shown once tests complete.

        Note: Custom test sciript paths and dependencies can be provided in
        $HPC_APPTESTS_DIR/tests_config.yaml. However, the test file itself must be
        adopted from /data/apps/test/apptests/run.sh. 
        """
    )
    parser.add_argument(
        "--version",
        action="version",
        version="""%(prog)s
                        Version: {version}""".format(
            version=config.__version
        ),
    )
    parser.add_argument(
        "-m",
        "--module",
        type=str,
        nargs='+', 
        required = False,
        help = """
                MODULE should not include the version. Runs test for all versions(s) of the MODULE provided. 
            """,
    )
    parser.add_argument(
        "-mv",
        "--moduleversion",
        nargs='+', 
        required = False,
        help = """
                MODULEVERSION: <module>/<version>. Runs test for the specific version of the module provided. 
            """,
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="verbose output"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="All", help="Output fields. Accepted fields are [Module,Dependency,Time,JobStatus,TestStatus,JobId,ExitCode,TestFile]"
    )

    if print_help:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    return args

def _setup_logging(debug, verbose):
    """Set the correct logging level."""
    logger.remove()
    if verbose:
        level = logging.INFO
    else:
        level = logging.WARN
    if debug:
        level = logging.DEBUG
        logger.add(sys.stderr, level=level)
        logger.debug("Debugging output enabled")
    else:
        logger.add(sys.stderr, level=level)
    logger.debug("Logging level set to : {}", level)

def checkTestStatus(jobId):
    '''
        Returns the status and the exit code of the job with jobId
    '''
    global testStatus
    cmd = ["sacct", "-j", jobId, "-n", "-p", "--format=State,ExitCode"]
    with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    ) as proc:
        res_stdout = proc.stdout.read()
        res_stderr = proc.stderr.read()
        testStatus[jobId] = [proc, res_stdout, res_stderr]

    subp = testStatus[jobId]
    while(subp[0].poll() is None):
        return ()
    status = subp[1].split('|')[0]
    if(subp[2] or status == "RUNNING"):
        return ()
    else:
        exitCode = ""
        try :
            exitCode = subp[1].split('|')[1]
        except:
            exitCode = ""

        return (status, exitCode)

def get_raw_json(args):
    '''
        Adopted from code written by Alex in /apps/lmod/admin/
        Returns a dict with lmod data
    '''
    spider = "/apps/lmod/lmod/libexec/spider"
    modulepath_root = os.environ["MODULEPATH"]

    print("Info: Reading latest lmod data from "+ modulepath_root)
    """Retrieve raw json data from either spider output or from a test file."""

    cmd = "{} -o spider-json {}".format(spider, modulepath_root)
    if args.debug:
        logger.debug("Cmd: '{}'".format(cmd))
    cmd_args = shlex.split(cmd)
    with subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
    ) as proc:
        res_stdout = proc.stdout.read().strip()
        res_stderr = proc.stderr.read()
    if res_stderr:
        print(
            "Error: the getent command call was not successful. Submit a support request"
        )
        if args.debug:
            logger.debug(res_stderr)
    if args.debug and args.verbose:
        logger.debug("stdout: '{}'".format(res_stdout))
    if not res_stdout:
        logger.error("Error: No output from the spider command.")
    raw_data = json.loads(res_stdout)
    if args.debug:
        logger.debug(raw_data)
    return raw_data

def checkJobStatus(args):
    '''
        Checks test status and updates the report
    '''
    global JobStatus
    global TestStatus

    # A thread that starts all test jobs and puts them in the config.RUNNING_TESTS list
    thread = threading.Thread(target=startTests(args))
    thread.start()
    thread.join()
    logger.debug("startTests Done")

    # A dict that keeps track of the completed tests so far
    testsCompleted = {}

    # Report is generated with the current timestamp
    report_name = time.strftime("%Y-%m-%d-%H_%M_%S")

    # Loops until all test jobs submitted complete with some status
    while(len(testsCompleted) <= len(config.RUNNING_TESTS)):
        logger.debug("The number of completed tests are: " + str(len(testsCompleted)) + "/" + str(len(config.RUNNING_TESTS)))
        logger.debug("The number of tests running are: " + str(len(config.RUNNING_TESTS) - len(testsCompleted)))

        # Processes the status of each job submitted and puts them appropriately in testsCompleted
        for job in config.RUNNING_TESTS:
            #  If module name is invalid or test file is missing, add this job to 'testsCompleted' with respective status
            if(job.module not in testsCompleted and (job.jobStatus == JobStatus.MISSING or job.jobStatus == JobStatus.INVALID)):
                logger.debug(job.jobStatus)
                remove_bash_code(job.filepath)
                testsCompleted[job.module + str(job.dependencies)] = ()
                continue
            # If job is submitted, check if there is any new status
            elif(job.jobStatus is not JobStatus.MISSING and job.proc.poll() is not None):
                if(job.proc.returncode == 0):
                    job.jobStatus = JobStatus.SUBMITTED
                    job.testStatus = TestStatus.RUNNING
                else :
                    job.jobStatus = JobStatus.FAILED
                    job.testStatus = TestStatus.NA

                # Process the job status
                jobId = job.jobOut.split()[3]
                job.jobId = jobId
                testStatus = checkTestStatus(jobId)
                if(len(testStatus) > 0):
                    job.exitCode = testStatus[1]
                    if(testStatus[0] == TestStatus.COMPLETED.value):
                        job.testStatus = TestStatus.COMPLETED
                    elif(testStatus[0] == TestStatus.FAILED.value):
                        job.testStatus = TestStatus.FAILED    

                    if(job.testStatus is not TestStatus.RUNNING and job.module not in testsCompleted):
                        remove_bash_code(job.filepath)
                        testsCompleted[job.module + str(job.dependencies)] = testStatus

        # After processing the entire batch of test jobs for new upates, genrate the latest report
        output.generateReport(report_name, args)
        if(len(testsCompleted) == len(config.RUNNING_TESTS)):
            output.generateReport(report_name, args, exit=True)
            print("Success: Program completed")
            print("Success: Check the report - /data/apps/tests/apptests/Reports/" + report_name + ".txt (.json also available)")
            print("Success: Check slurm logs for a particular test - /data/apps/tests/apptests/slurm_logs/<job_id>.log\n")
            logger.debug("Waiting for thread2")
            sys.exit(0)

def append_bash_code(file_path):
    bash_code = '''
# BEGIN
set -o errtrace
trap 'catch $?' ERR
catch() {
echo "apptests caught an error:"
if [ "$1" != "0" ]; then
    echo "Error code $1. Terminating!"
    exit $1
fi
}

modules="ml"

for module in "$@"; do
modules+=" $module"
done
module purge .

eval "$modules"
# END
    '''
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    addedTrap = False

    for line in lines:
        if addedTrap or line.startswith('#'):
            modified_lines.append(line)
        else:
            modified_lines.append(bash_code + '\n')
            addedTrap = True

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def remove_bash_code(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    print(lines)
    modified_lines = []
    inTrapBlock = False

    for line in lines:
        if line.startswith('# BEGIN'):
            inTrapBlock = True
        if line.startswith('# END'):
            inTrapBlock = False
            continue

        if not inTrapBlock:
            modified_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

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
            if(os.path.exists(testFilePath)):
                cmd = ['sbatch', testFilePath]

                append_bash_code(testFilePath)

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

def startTests(args): 
    '''
        Loads lmod data, custom yaml configs and calls submitJob() for the module(s) to be tested
    '''

    # Reading module list from spider  
    lmod = get_raw_json(args)

    '''Alternate way to read lmod data, make sure to refresh the file with latest data first'''
    #with open("/apps/apptests/lmod_spider_output.txt") as fh:
    #   lmod = json.load(fh)
    #  print("Warning: Using lmod data from lmod_spider_output.txt which might be outdated")
    
    # Reading test configurations from tests_config.yaml
    with open("/apps/apptests/tests_config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.debug(exc)
            print("YAML config file error. Please check the file.")

    # Tests all versions of the specified modules
    if(args.module):
        for module in args.module:    
            logger.debug(module)      
            submitJob(lmod, config, module)
    
    # Tests a specific module/version 
    if(args.moduleversion):
        for arg in args.moduleversion:
            logger.debug(arg) 
            submitJob(lmod, config, arg.split('/')[0], arg)
                 

def main():
    args = parse_args()

    if not (args.module or args.moduleversion):
        print("'-m' or '-mv' flags required. Please specify atleast one module to test. See help with '-h' flag for help.")
        exit(1)

    if args.output :
        outputFields = args.output.split(",")
        for outputField in outputFields:
            if outputField not in config.OUTPUT_FIELDS:
                print(f"'{outputField}' is an invalid field name. See help with '-h' flag for more details.")
                exit(1)
        args.output = outputFields
        
    _setup_logging(args.debug, args.verbose)
    logger.debug(args.module)

    print("Info: Testing is about to begin. This may take a while to finish.")
    checkJobStatus(args)

if __name__ == '__main__' :
    main()
