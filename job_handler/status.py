import sys
import time
import subprocess
from loguru import logger

import config
from report_handler import report_generator
from job_handler import JobStatus, TestStatus

testStatus = {}

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

def checkJobStatus(args):
    '''
        Checks test status and updates the report
    '''
    global JobStatus
    global TestStatus

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
                # if(os.path.exists(job.filepath)):
                #     removeTrap(job.filepath)
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
                        # removeTrap(job.filepath)
                        testsCompleted[job.module + str(job.dependencies)] = testStatus

        # After processing the entire batch of test jobs for new upates, genrate the latest report
        report_generator.generate_report(report_name, args)
        if(len(testsCompleted) == len(config.RUNNING_TESTS)):
            report_generator.generate_report(report_name, args, exit=True)
            print("Success: Program completed")
            print("Success: Check the report - /data/apps/tests/apptests/Reports/" + report_name + ".txt (.json also available)")
            print("Success: Check slurm logs for a particular test - /data/apps/tests/apptests/slurm_logs/<job_id>.log\n")
            sys.exit(0)