import sys
import time
import pwd
import os
import subprocess
from loguru import logger
from rich.progress import Progress

import config
from report_handler import report_generator
from test_handler.test import JobStatus, TestStatus, Test
from test_handler.apptest import AppTest

def cancelJob(job_id):
    cmd = ["scancel", job_id]
    with subprocess.Popen(
                cmd
    ) as proc:
        proc.wait()
    
    return True if proc.returncode is not None else False

def get_test_status(job_id):
    '''
        Returns the status and the exit code of the job with job_id
    '''
    cmd = ["sacct", "-j", job_id, "-n", "-p", "--format=State,ExitCode"]
    with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    ) as proc:
        res_stdout, res_stderr = proc.communicate()
        # res_stderr = proc.stderr.read()

    logger.debug([proc, res_stdout, res_stderr])

    # No output on SACCT
    while(proc.poll() is None or res_stdout == ''):
        proc.kill()
        return None
    
    # Parse SACCT output for status and exitcode
    status, exitCode = '', ''
    try:
        # Todo: Handle stderr better
        # sacct error (invalid jobid etc)
        if(res_stderr):
            proc.kill()
            return None
        
        # String processing can be out of bounds
        status = res_stdout.split('\n')[0].split('|')[0]
        exitCode = res_stdout.split('\n')[0].split('|')[1]  
    except:
        logger.debug("SACCT output for " + str(job_id) + " couldn't be parsed!")

    proc.kill()
    return (status, exitCode)

def kill_test(job_id):
    cmd = ["scancel", job_id]
    with subprocess.Popen(
                cmd
    ) as proc:
        proc.poll()
    
    return True if proc.returncode is not None else False

def check_timeout(curr_test: Test):
    job_runtime = 0
    if curr_test.endTime is not None and curr_test.startTime is not None:
        job_runtime = curr_test.endTime - curr_test.startTime
    elif curr_test.startTime is not None:
        job_runtime = time.time() - curr_test.startTime

    if job_runtime > config.MAX_TEST_RUNTIME:
        return True
    return False

def verify_SLURM_status(AppTest_Instance: AppTest, curr_test: Test):
    '''
     Initially;                JobStatus -> PENDING,           TestStatus -> -
     If Invalid input;         JobStatus -> INVALID MODULE,    TestStatus -> -
     If missing test files;    JobStatus -> MISSING,           TestStatus -> -
     If SBATCH Fails           JobStatus -> FAILED,            TestStatus -> -
    '''
    if(curr_test.jobStatus == JobStatus.MISSING or curr_test.jobStatus == JobStatus.INVALID):
        logger.debug(curr_test.jobStatus)
        # Todo: Remove the temp job scripts with TRAP

        return False

    # If job is submitted via SBATCH
    if(curr_test.proc.poll() is not None):
        # Check SBATCH return code
        if(curr_test.proc.returncode == 0):
            curr_test.jobStatus = JobStatus.PENDING
            curr_test.testStatus = TestStatus.NA
        else :
            curr_test.jobStatus = JobStatus.FAILED
            curr_test.testStatus = TestStatus.NA
            return False
        
        # Set job id from SBATCH
        curr_test.jobId = curr_test.jobOut.split()[3]
    
    return True

def update_status(curr_test: Test, curr_test_status: tuple):
    '''
    ======================== Note on status ==================================================
     Initially;                JobStatus -> PENDING,           TestStatus -> -
     If Invalid input;         JobStatus -> INVALID MODULE,    TestStatus -> -
     If missing test files;    JobStatus -> MISSING,           TestStatus -> -
     If SBATCH Fails           JobStatus -> FAILED,            TestStatus -> -
     After a job is RUNNING;   JobStatus -> SUBMITTED,         TestStatus -> RUNNING    
     If a job is COMPLETED     JobStatus -> SUBMITTED (-),     TestStatus -> COMPLETED
     If a job is FAILED        JobStatus -> SUBMITTED (-),     TestStatus -> FAILED

     If a job exceeds 
     MAX_TEST_RUNTIME          JobStatus -> TIMEOUT,           TestStatus -> KILLED

     ===========================================================================================
    '''

    (SACCT_job_status, SACCT_exit_code) = curr_test_status
    
    # https://slurm.schedmd.com/squeue.html#SECTION_JOB-STATE-CODES
    # Todo: Test and add more status
    logger.debug("SACCT_job_status is :" + SACCT_job_status)

    if SACCT_job_status == "PENDING" or SACCT_job_status == "":
        curr_test.jobStatus = JobStatus.PENDING
        curr_test.testStatus = TestStatus.NA
    elif SACCT_job_status in ("RUNNING", "COMPLETING"):
        # Set start time if moving to RUNNING state for timeout monitoring
        if(curr_test.jobStatus == JobStatus.PENDING):
            curr_test.startTime = time.time()
        curr_test.jobStatus = JobStatus.SUBMITTED
        curr_test.testStatus = TestStatus.RUNNING
    
    elif SACCT_job_status == "COMPLETED":
        curr_test.jobStatus = JobStatus.SUBMITTED
        curr_test.testStatus = TestStatus.COMPLETED
    
    elif SACCT_job_status == "FAILED":
        curr_test.testStatus = TestStatus.FAILED

    elif SACCT_job_status in ("CANCELLED", "DEADLINE", "TIMEOUT"):
        curr_test.testStatus = TestStatus.CANCELLED

    else:
        curr_test.testStatus = TestStatus.SLURMERROR
    
    if SACCT_job_status not in ("PENDING", "RUNNING", "COMPLETING"): 
        # Todo: Get exit code from SACCT again?
        curr_test.exitCode = SACCT_exit_code
        curr_test.endTime = time.time()

def checkJobStatus(args, AppTest_Instance):
    '''
        Checks test status and updates the report

        ======================== Note on status ==================================================
        Initially;                JobStatus -> PENDING,           TestStatus -> -
        If Invalid input;         JobStatus -> INVALID MODULE,    TestStatus -> -
        If missing test files;    JobStatus -> MISSING,           TestStatus -> -
        If SBATCH Fails           JobStatus -> FAILED,            TestStatus -> -
        After a job is RUNNING;   JobStatus -> SUBMITTED,         TestStatus -> RUNNING    
        If a job is COMPLETED     JobStatus -> SUBMITTED (-),     TestStatus -> COMPLETED
        If a job is FAILED        JobStatus -> SUBMITTED (-),     TestStatus -> FAILED

        If a job exceeds 
        MAX_TEST_RUNTIME          JobStatus -> TIMEOUT,           TestStatus -> KILLED

        ===========================================================================================
    
    '''

    total_test_count = AppTest_Instance.get_total_test_count()

    # Report is generated with the current timestamp
    report_name = time.strftime("%Y-%m-%d-%H_%M_%S")
    print("Results in: /data/apps/tests/apptests/Reports/" + report_name + ".txt (.json also available)")

    with Progress(transient=True) as progress:
        progress_bar = progress.add_task("[cyan]Running Tests ...", total=total_test_count)
        # Loops until all test jobs submitted complete with some status
        while(AppTest_Instance.get_completed_tests_count() < total_test_count):
            logger.debug("The number of completed tests are: " + str(AppTest_Instance.get_completed_tests_count()) + "/" + str(total_test_count))
            logger.debug("The number of tests running are: " + str(total_test_count - AppTest_Instance.get_completed_tests_count()))
            logger.debug(AppTest_Instance.get_completed_tests())

            # Processes the status of each test submitted as a job
            for curr_test in AppTest_Instance.get_running_tests():

                curr_test_id = curr_test.module + str(curr_test.dependencies)
                logger.debug(curr_test_id)

                # Check if current test has completed
                if curr_test_id in AppTest_Instance.get_completed_tests():
                    continue

                # Check if SBATCH failed
                if verify_SLURM_status(AppTest_Instance, curr_test) is False:
                    logger.debug(curr_test.jobStatus)
                    logger.debug(curr_test.testStatus)
                    AppTest_Instance.add_completed_test(curr_test_id, curr_test)
                    progress.update(progress_bar, advance=1)
                    continue
                
                # Check if current test exceeded timeout interval
                if check_timeout(curr_test):
                    kill_test(curr_test.jobId)
                    curr_test.jobStatus = JobStatus.TIMEOUT
                    curr_test.testStatus = TestStatus.KILLED
                    continue
                
                # Get job status from SACCT
                curr_test_status = get_test_status(curr_test.jobId)
                logger.debug(curr_test_status)

                if curr_test_status is not None:
                    update_status(curr_test, curr_test_status)

                if curr_test.testStatus not in (TestStatus.RUNNING, TestStatus.NA):
                    # removeTrap(job.filepath)
                    logger.debug(curr_test.jobStatus)
                    logger.debug(curr_test.testStatus)
                    AppTest_Instance.add_completed_test(curr_test_id, curr_test)
                    progress.update(progress_bar, advance=1)

            report_generator.generate_report(AppTest_Instance, report_name, args)
        # After processing the entire batch of test jobs for new upates, genrate the latest report
        if(AppTest_Instance.get_completed_tests_count() == total_test_count):
            report_generator.generate_report(AppTest_Instance, report_name, args, exit=True)
            print("Success: Program completed")
            print("Success: Check the report - /data/apps/tests/apptests/Reports/" + report_name + ".txt (.json also available)")
            print("Success: Check slurm logs for a particular test - /data/apps/tests/apptests/slurm_logs/<job_id>.log\n")
            
            sys.exit(0)