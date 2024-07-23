"""
    This framework will run tests on specified modules and provide a report
    Author: Sohaib Uddin Syed (sohaibuddinsyed@ufl.edu/syedsohaib074@gmail.com)
"""

import argparse
import sys
import logging
from loguru import logger

import config
from job_handler import tester
from test_handler.apptest import AppTest

# Arg parsers setup for rcapptests bin
def parse_args(print_help=False):
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write("error: %s\n" % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        usage="apptests [options] [group]",
        description="""
        
        Internal tool to run application tests.

        How to test an application:
        1) Create a test script in /data/apps/test/<app> where 'app' is the 
        application to be tested.
        2) Modify the test script as needed.
        3) Run the tests. (Eg: apptests -m <app>, apptests -mv app/version etc)
        4) Check the report and slurm_logs in /data/apps/test/apptests/, full
        paths will be shown once tests complete.

        Note: Custom test sciript paths and dependencies can be provided in
        $HPC_APPTESTS_DIR/tests_config.yaml.
        """
    )
    parser.add_argument(
        "--version",
        action="version",
        version="""%(prog)s
                        Version: {version}""".format(
            version=config.__version
        ),
    )
    parser.add_argument(
        "-m",
        "--module",
        type=str,
        nargs='+', 
        required = False,
        help = """
                MODULE should not include the version. Runs test for all versions(s) of the MODULE provided. 
            """,
    )
    parser.add_argument(
        "-mv",
        "--moduleversion",
        nargs='+', 
        required = False,
        help = """
                MODULEVERSION: <module>/<version>. Runs test for the specific version of the module provided. 
            """,
    )
    parser.add_argument(
        "-testall",
        "--testall",
        action="store_true",
        default=False,
        help = """
                Runs tests for all modules in the system.
            """,
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="verbose output"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="All", help="Output fields. Accepted fields are [Module,Dependency,TestFile,Time,JobId,SlurmLogs,JobStatus,TestStatus,ExitCode]"
    )

    if print_help:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    return args

def _setup_logging(debug, verbose):
    """Set the correct logging level."""
    logger.remove()
    if verbose:
        level = logging.INFO
    else:
        level = logging.WARN
    if debug:
        level = logging.DEBUG
        logger.add(sys.stderr, level=level)
        logger.debug("Debugging output enabled")
    else:
        logger.add(sys.stderr, level=level)
    logger.debug("Logging level set to : {}", level)

def main():
    args = parse_args()

    # Validate mandatory options
    if not (args.testall or args.module or args.moduleversion):
        print("'-testall or -m' or '-mv' flags required. Please specify atleast one module to test. See help with '-h' flag for help.")
        exit(1)

    # Validate the output column flags
    if args.output :
        args_output_fields = args.output.split(",")
        for output_field in args_output_fields:
            if output_field not in config.OUTPUT_FIELDS:
                print(f"'{output_field}' is an invalid field name. See help with '-h' flag for more details.")
                exit(1)
        args.output = args_output_fields
        
    _setup_logging(args.debug, args.verbose)
    logger.debug(args.module)

    print("Info: Testing is about to begin. This may take a while to finish.")

    # Create an app test instace
    AppTest_Instance = AppTest()

    # Start tests
    tester.start_tests(args, AppTest_Instance)

if __name__ == '__main__' :
    main()