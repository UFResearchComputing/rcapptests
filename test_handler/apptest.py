from test_handler.test import Test

class AppTest(object):
    # A list of submitted tests
    RUNNING_TESTS = []
    # A dict that keeps track of the completed tests so far
    COMPLETED_TESTS = {}   

    def __init__(self):
        pass

    def get_total_test_count(self):
        return len(self.RUNNING_TESTS)
    
    def get_running_tests(self):
        return self.RUNNING_TESTS

    def add_test(self, test: Test):
        self.RUNNING_TESTS.append(test)
    
    def get_completed_tests_count(self):
        return len(self.COMPLETED_TESTS)
    
    def get_completed_tests(self):
        return self.COMPLETED_TESTS
    
    def add_completed_test(self, key: str, completed_Test: Test):
        self.COMPLETED_TESTS[key] = completed_Test
