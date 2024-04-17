import time
from enum import Enum

class JobStatus(Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    MISSING= "NO TESTS"
    INVALID = "INVALID MODULE"

class TestStatus(Enum):
    NA = "-"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    CANCELLED = "CANCELLED"
    KILLED = "KILLED"
    SLURMERROR = "SLURMERROR"

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
    
    @staticmethod 
    def new_test(module_version, dependencies, test_file_path, proc, res_stdout, res_stderr):
        return Test(module_version, dependencies, test_file_path, None, None, 'N/A', proc, JobStatus.PENDING, res_stdout, res_stderr, TestStatus.NA, "-")

    @staticmethod 
    def missing_test(module_version, dependencies, test_file_path):
        return Test(module_version, dependencies, test_file_path, time.time(), None, 'N/A', None, JobStatus.MISSING, None, None, TestStatus.NA, "-")
    
    @staticmethod
    def invalid_test(module):
        return Test(module, "-", "-", time.time(), time.time(), 'N/A', None, JobStatus.INVALID, None, None, TestStatus.NA, "-")
