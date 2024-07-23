"""
   This script will generate report for tests
   Author: Sohaib Uddin Syed (sohaibuddinsyed@ufl.edu/syedsohaib074@gmail.com)
"""

import time
import json
from loguru import logger
from datetime import datetime
from rich.console import Console
from rich.table import Table

import config
from test_handler.test import JobStatus, TestStatus

class Color:
    UNAVAILABLE = "[blue]"
    INPROGRESS = "[cyan]"
    SUCCESS = "[green]"
    WARNING = "[yellow]"
    FAIL = "[red]"

def generate_failed_data(invalid_input_cnt, tests_missing_cnt):
    '''
        Generates and populates wrong/missing inputs test summary
    '''
    # Invalid jobs and tests summary
    failed_table = Table(title="Wrong/missing inputs")        
    failed_table.add_column("Invalid Modules", justify="center", style="red")
    failed_table.add_column("Missing Test files", justify="center", style="red")
    failed_table.add_row(str(invalid_input_cnt), str(tests_missing_cnt))
    return failed_table

def generate_summary_data(jobs_submitted_cnt, tests_passed_cnt, tests_failed_cnt):
    '''
        Generates and populates test result summary in the summary table
    '''
    # Summary of the main table
    summary_table = Table(title="Test Summary - Modules which were tested")
    summary_table.add_column("Total jobs submitted", justify="center")
    summary_table.add_column("Tests Passed", justify="center", style="green")
    summary_table.add_column("Tests Failed", justify="center", style="red")
    summary_table.add_row(str(jobs_submitted_cnt), str(tests_passed_cnt), str(tests_failed_cnt))
    return summary_table

def generate_report_data(AppTest_Instance, table, report_name, args):
    '''
        Populates test result in the main table,
        Generates .txt and .json report files
    '''
    add_all_columns = True if "All" in args.output else False
    json_dict = {}

    # Variables to track various metrics
    tests_passed_cnt, tests_failed_cnt, jobs_submitted_cnt, invalid_input_cnt, tests_missing_cnt = 0, 0, 0, 0, 0

    # Process each test status and generate row data
    test_idx = 0
    for curr_test in AppTest_Instance.get_running_tests():
        curr_row = []
        curr_json_obj = {}
        
        # Process job status
        job_color = Color.FAIL
        if curr_test.job_status == JobStatus.SUBMITTED:
            job_color = Color.SUCCESS
            jobs_submitted_cnt += 1
        elif curr_test.job_status == JobStatus.PENDING:
            job_color = Color.INPROGRESS
        elif curr_test.job_status == JobStatus.INVALID:
            invalid_input_cnt += 1
        elif curr_test.job_status == JobStatus.MISSING:
            tests_missing_cnt += 1
            job_color = Color.WARNING
        # elif curr_test.end_time is None:
        #     curr_test.end_time = time.time()

        # Process test status
        testColor = Color.FAIL
        if curr_test.test_status == TestStatus.RUNNING:
            testColor = Color.INPROGRESS
        elif curr_test.test_status == TestStatus.NA:
            testColor = Color.UNAVAILABLE
        elif curr_test.test_status == TestStatus.COMPLETED:
            tests_passed_cnt += 1
            testColor = Color.SUCCESS
            # if curr_test.end_time is None:
            #     curr_test.end_time = time.time()
        else: 
            tests_failed_cnt += 1
            # if curr_test.end_time is None:
            #     curr_test.end_time = time.time()

        # Calculate duration
        elapsedSeconds = 0
        if curr_test.end_time is not None and curr_test.start_time is not None:
            elapsedSeconds = curr_test.end_time - curr_test.start_time
        elif curr_test.start_time is not None:
            elapsedSeconds = time.time() - curr_test.start_time

        elapsedTime = time.strftime('%H:%M:%S', time.gmtime(elapsedSeconds))
        
        # Append all data as a row
        moduleName = curr_test.module
        curr_row.append(str(test_idx + 1))

        if add_all_columns or "Module" in args.output:
            curr_row.append(moduleName)
            curr_json_obj["Module"] = moduleName

        if add_all_columns or "Dependency" in args.output:
            curr_row.append(curr_test.dependencies) 
            curr_json_obj["Dependency"] = curr_test.dependencies

        if add_all_columns or "TestFile" in args.output:
            curr_row.append("$TESTS_DIR/" + curr_test.file_path)
            curr_json_obj["TestFile"] = "$TESTS_DIR/" +  curr_test.file_path

        if add_all_columns or "Time" in args.output:
            curr_row.append(f"{elapsedTime}") 
            curr_json_obj["Time"] = elapsedTime

        if add_all_columns or "JobId" in args.output:
            curr_row.append(curr_test.job_id)
            curr_json_obj["JobId"] = curr_test.job_id

        if add_all_columns or "SlurmLog" in args.output:
            curr_row.append("$SLURMLOGS_DIR/" + curr_test.job_id + ".log")
            curr_json_obj["SlurmLog"] = "$SLURMLOGS_DIR/" + curr_test.job_id

        if add_all_columns or "JobStatus" in args.output:
            curr_row.append(job_color + f"{curr_test.job_status.value}")
            curr_json_obj["JobStatus"] = curr_test.job_status.value

        if add_all_columns or "TestStatus" in args.output:
            curr_row.append(testColor + f"{curr_test.test_status.value}")
            curr_json_obj["TestStatus"] = curr_test.test_status.value

        if add_all_columns or "ExitCode" in args.output:
            curr_row.append(testColor + f"{curr_test.exit_code}")
            curr_json_obj["ExitCode"] = curr_test.exit_code

        # Add row into the table and json file
        table.add_row(*curr_row)
        json_dict["sno_" + str(test_idx + 1)] = curr_json_obj
        test_idx += 1

    # Generate summary after the report is complete
    summaryTable = generate_summary_data(jobs_submitted_cnt, tests_passed_cnt, tests_failed_cnt)
    failedTable = generate_failed_data(invalid_input_cnt, tests_missing_cnt)
    
    with open(report_name + ".json", "wt") as json_file:
        json_file.write(json.dumps(json_dict, indent=4))

    return table, summaryTable, failedTable

def generate_report_schema(args):
    '''
        Generate schema for the report table
    '''

    add_all_columns = True if "All" in args.output else False
    table = Table(min_width=200)

    table.add_column("Sno", justify="left", style="cyan", no_wrap=True)

    if add_all_columns or "Module" in args.output:
        table.add_column("Module/Version", style="magenta", no_wrap=True)

    if add_all_columns or "Dependency" in args.output:
        table.add_column("Dependencies", style="green",no_wrap=True)

    if add_all_columns or "TestFile" in args.output:
        table.add_column("Test File", style="cyan")

    if add_all_columns or "Time" in args.output:
        table.add_column("Duration", style="magenta", no_wrap=True)

    if add_all_columns or "JobId" in args.output:
        table.add_column("Job Id", style="green", no_wrap=True)

    if add_all_columns or "SlurmLog" in args.output:
        table.add_column("Slurm Logs", style="green", no_wrap=True)

    if add_all_columns or "JobStatus" in args.output:
        table.add_column("Job Status", style="cyan", no_wrap=True)

    if add_all_columns or "TestStatus" in args.output:
        table.add_column("Test Status", no_wrap=True)

    if add_all_columns or "ExitCode" in args.output:
        table.add_column("Exit Code", style="green", no_wrap=True)
    
    return table

def generate_report(AppTest_Instance, testStartTime, args, exit=False):
    '''
        Driver method to generate report (.txt, .json) with all the required tables
    '''
    report_name = config.REPORT_PATH + testStartTime
    with open(report_name + ".txt", "wt") as report_file:
        console = Console(file=report_file, width=750)

        # Report headers
        if not exit:
            console.print("Test Status: Testing is in progress...... (Reload file for new results)\n")
        else:
            console.print("Test Status: Testing Complete!\n")
        console.print(f"Test Report : {datetime.now()}")

        # Generate main table schema
        table = generate_report_schema(args)

        # Populate main table along with summary and failed status tables
        table, summaryTable, failedTable = generate_report_data(AppTest_Instance, table, report_name, args)

        # Write all tables to .txt file
        console.print(table)
        console.print(summaryTable)
        console.print(failedTable)

        logger.debug("Latest report generated in $REPORTS_DIR/" + testStartTime + ".txt")