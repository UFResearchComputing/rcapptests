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
TEST_CONFIG = "/apps/apptests/tests_config.yaml"
TRAP_FILE = "/apps/apptests/job_handler/trap.sh"
TEMP_TEST_FILE = '/data/apps/tests/apptests/temp/'
REPORT_PATH = "/data/apps/tests/apptests/Reports/"
RUNNING_TESTS = []
OUTPUT_FIELDS = ["All", "Module", "Dependency", "Time", "JobStatus", "TestStatus", "JobId", "ExitCode", "TetFile"]