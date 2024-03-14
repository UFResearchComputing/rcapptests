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