"""
    This framework will run tests on specified modules and provides a report
    Author: Sohaib Uddin Syed (sohaibuddinsyed@ufl.edu), June 2023 - Present
"""

import argparse
import sys
# TODO: Move config to a toml config file e.g. rcappstests.toml
import config
from job_handler import tester
from test_handler.apptest import AppTest
from rcapptests.common import _setup_logging
from rcapptests.common import _get_config

VERBOSE = False
DEBUG = False
CONFIG_FILENAME = "rcappstests.toml"
CONFIG_VARIABLE = "RCAPPSTESTS_CONF"


def _parse_args(print_help=False):
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write("error: %s\n" % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        usage="%(prog)s [options] [group]",
        description="""
        Internal tool to run application tests.

        How to test an application:
        1) Create a test script in /data/apps/test/<app> where 'app' is the application to be tested
        2) Modify the test script as needed
        3) Run the tests. (Eg: apptests -m <app>, apptests -mv app/version etc)
        4) Check the report and slurm_logs in /data/apps/test/apptests/, full
        paths will be shown once tests complete
        Note: Custom test script paths and dependencies can be provided in
        $APPTESTS_DIR/tests_config.yaml.
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
        required=False,
        help=""" MODULE should not include the version. Runs test for all versions(s) of the MODULE
        provided. """,
    )
    parser.add_argument(
        "-mv",
        "--moduleversion",
        nargs='+',
        required=False,
        help="""MODULEVERSION: <module>/<version>. Runs test for the specific version of the module
        provided.""",
    )
    parser.add_argument(
        "-testall",
        "--testall",
        action="store_true",
        default=False,
        help=""" Runs tests for all modules in the system""",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="verbose output"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="All",
        help="""Output fields. Accepted fields are
        [Module,Dependency,Time,JobStatus,TestStatus,JobId,ExitCode,TestFile]""")

    args = parser.parse_args()
    if print_help:
        parser.print_help()
        sys.exit(0)
    if not (args.testall or args.module or args.moduleversion):
        print_help = True
    return args


def main():
    global DEBUG, VERBOSE
    args = _parse_args()
    logger = _setup_logging(args.debug, args.verbose)
    config = _get_config(args.config, CONFIG_FILENAME, CONFIG_VARIABLE)
    if args.output:
        output_fields = args.output.split(",")
        for output_field in output_fields:
            if output_field not in config.OUTPUT_FIELDS:
                print(f"'{output_field}' is an invalid config field name")
                exit(1)
    if args.module:
        logger.debug(f"Testing module {args.module}")

    if VERBOSE:
        print("Info: Testing is about to begin. This may take a while to finish.")

    AppTest_Instance = AppTest()
    tester.startTests(args, AppTest_Instance)


if __name__ == '__main__':
    main()

