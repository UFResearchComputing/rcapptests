import config
from loguru import logger
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
import json

JobStatus = config.JobStatus
TestStatus = config.TestStatus

class Color:
    UNAVAILABLE = "[blue]"
    INPROGRESS = "[cyan]"
    SUCCESS = "[green]"
    WARNING = "[yellow]"
    FAIL = "[red]"

def generateReport(testStartTime, args, exit=False):
    test_data = {}
    report_name = "/data/apps/tests/apptests/Reports/" + testStartTime
    with open(report_name + ".txt", "wt") as report_file:
        console = Console(file=report_file)

        if not exit:
            console.print("Test Status: Testing is in progress...... (Reload file for new results)\n")
        else:
            console.print("Test Status: Testing Complete!\n")

        console.print(f"Test Report : {datetime.now()}")
        printAll = False
        if "All" in args.output:
            printAll = True

        table = Table(min_width=200)

        table.add_column("Sno", justify="left", style="cyan", no_wrap=True)

        if printAll or "Module" in args.output:
            table.add_column("Module/Version", style="magenta", no_wrap=True)

        if printAll or "Dependency" in args.output:
            table.add_column("Dependencies", style="green",no_wrap=True)

        if printAll or "TestFile" in args.output:
            table.add_column("Test File", style="cyan")

        if printAll or "Time" in args.output:
            table.add_column("Duration", style="magenta", no_wrap=True)

        if printAll or "JobId" in args.output:
            table.add_column("Job Id", style="green", no_wrap=True)

        if printAll or "JobStatus" in args.output:
            table.add_column("Job Status", style="cyan", no_wrap=True)

        if printAll or "TestStatus" in args.output:
            table.add_column("Test Status", no_wrap=True)

        if printAll or "ExitCode" in args.output:
            table.add_column("Exit Code", style="green", no_wrap=True)

        passed = 0
        failed = 0
        jobsSubmitted = 0
        invalid = 0
        missingTests = 0

        for i in range(len(config.RUNNING_TESTS)):
            row = []
            data = {}
            test = config.RUNNING_TESTS[i]
            
            jobColor = Color.FAIL
            if test.jobStatus == JobStatus.SUBMITTED:
                jobColor = Color.SUCCESS
                jobsSubmitted += 1
            elif test.jobStatus == JobStatus.PENDING:
                jobColor = Color.INPROGRESS
            elif test.jobStatus == JobStatus.INVALID:
                invalid += 1
            elif test.jobStatus == JobStatus.MISSING:
                missingTests += 1
                jobColor = Color.WARNING
            elif test.endTime is None:
                test.endTime = time.time()

            testColor = Color.FAIL
            if test.testStatus == TestStatus.RUNNING:
                testColor = Color.INPROGRESS
            elif test.testStatus == TestStatus.NA:
                testColor = Color.UNAVAILABLE
            elif test.testStatus == TestStatus.COMPLETED:
                passed += 1
                testColor = Color.SUCCESS
                if test.endTime is None:
                    test.endTime = time.time()
            elif test.testStatus == TestStatus.FAILED:
                failed += 1
                if test.endTime is None:
                    test.endTime = time.time()

            if test.endTime is not None:
                elapsedSeconds = test.endTime - test.startTime
            else:
                elapsedSeconds = time.time() - test.startTime

            elapsedTime = time.strftime('%H:%M:%S', time.gmtime(elapsedSeconds))
            
            moduleName = test.module
            row.append(str(i + 1))

            if printAll or "Module" in args.output:
                row.append(moduleName)
                data["Module"] = moduleName

            if printAll or "Dependency" in args.output:
                row.append(test.dependencies) 
                data["Dependency"] = test.dependencies

            if printAll or "TestFile" in args.output:
                row.append(test.filepath)
                data["TestFile"] = test.filepath

            if printAll or "Time" in args.output:
                row.append(f"{elapsedTime}") 
                data["Time"] = elapsedTime

            if printAll or "JobId" in args.output:
                row.append(test.jobId)
                data["JobId"] = test.jobId

            if printAll or "JobStatus" in args.output:
                row.append(jobColor + f"{test.jobStatus.value}")
                data["JobStatus"] = test.jobStatus.value

            if printAll or "TestStatus" in args.output:
                row.append(testColor + f"{test.testStatus.value}")
                data["TestStatus"] = test.testStatus.value

            if printAll or "ExitCode" in args.output:
                row.append(testColor + f"{test.exitCode}")
                data["ExitCode"] = test.exitCode
        
            table.add_row(*row)
            test_data["sno_" + str(i + 1)] = data

        with open(report_name + ".json", "wt") as json_file:
            json_file.write(json.dumps(test_data, indent=4))


        summaryTable = Table(title="Test Summary - Modules which were tested")
        summaryTable.add_column("Total jobs submitted", justify="center")
        summaryTable.add_column("Tests Passed", justify="center", style="green")
        summaryTable.add_column("Tests Failed", justify="center", style="red")
        summaryTable.add_row(str(jobsSubmitted), str(passed), str(failed))

        failedTable = Table(title="Wrong/missing inputs")        
        failedTable.add_column("Invalid Modules", justify="center", style="red")
        failedTable.add_column("Missing Test files", justify="center", style="red")
        failedTable.add_row(str(invalid), str(missingTests))

        
        console.print(table)
        console.print(summaryTable)
        console.print(failedTable)

        logger.debug("Latest report generated in " + report_name)
