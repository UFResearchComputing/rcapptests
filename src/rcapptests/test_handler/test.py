import time
from enum import Enum

'''
    Enums to denote Job and Test statuses
'''
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
    '''
        This class represents all the data associated with a test. 
        The framework manages all the tests as instances of this class
    '''
    def __init__(self, module, dependencies, file_path, start_time, end_time,  job_id, proc, job_status, job_out, job_err, test_status, exit_code):
        self.module = module
        self.dependencies = dependencies
        self.file_path = file_path
        self.start_time = start_time
        self.end_time = end_time
        self.job_id = job_id
        self.proc = proc
        self.job_status = job_status
        self.job_out = job_out
        self.job_err = job_err
        self.test_status = test_status
        self.exit_code = exit_code
    
    @staticmethod 
    def new_test(module_version, dependencies, test_file_path, proc, res_stdout, res_stderr):
        return Test(module_version, dependencies, test_file_path, None, None, 'N/A', proc, JobStatus.PENDING, res_stdout, res_stderr, TestStatus.NA, "-")

    @staticmethod 
    def missing_test(module_version, dependencies, test_file_path):
        return Test(module_version, dependencies, test_file_path, time.time(), None, 'N/A', None, JobStatus.MISSING, None, None, TestStatus.NA, "-")
    
    @staticmethod
    def invalid_test(module):
        return Test(module, "-", "-", time.time(), time.time(), 'N/A', None, JobStatus.INVALID, None, None, TestStatus.NA, "-")
