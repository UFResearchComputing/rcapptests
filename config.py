from enum import Enum

class JobStatus(Enum):
    MISSING= "NO TESTS"
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FAILED = "FAILED"
    INVALID = "INVALID MODULE"

class TestStatus(Enum):
    NA = "-"
    MISSING= "-"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    
__version = "1.0.0"
TEST_PATH = "/data/apps/tests/"
STATIC_OUTPUT = ""
DYNAMIC_OUTPUT = ""
RUNNING_TESTS = []
OUTPUT_FIELDS = ["All", "Module", "Dependency", "Time", "JobStatus", "TestStatus", "JobId", "ExitCode", "TetFile"]
