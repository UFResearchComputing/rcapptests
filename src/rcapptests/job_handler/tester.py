import os
import yaml
import subprocess
import shlex
import json
from loguru import logger 

from rcapptests.job_handler import dispatcher, status

def get_raw_json(args):
    '''
        Adopted from code written by Alex (om@rc.ufl.edu) in /apps/lmod/admin/
        Returns a dict with lmod data
    '''
    spider = "/apps/lmod/lmod/libexec/spider"
    modulepath_root = os.environ["MODULEPATH"]

    print("Info: Reading latest lmod data from "+ modulepath_root)
    """Retrieve raw json data from either spider output or from a test file."""

    cmd = "{} -o spider-json {}".format(spider, modulepath_root)
    if args.debug:
        logger.debug("Cmd: '{}'".format(cmd))
    cmd_args = shlex.split(cmd)
    with subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
    ) as proc:
        res_stdout = proc.stdout.read().strip()
        res_stderr = proc.stderr.read()
    if res_stderr:
        print(
            "Error: the getent command call was not successful. Submit a support request"
        )
        if args.debug:
            logger.debug(res_stderr)
    if args.debug and args.verbose:
        logger.debug("stdout: '{}'".format(res_stdout))
    if not res_stdout:
        logger.error("Error: No output from the spider command.")
    raw_data = json.loads(res_stdout)
    if args.debug:
        logger.debug(raw_data)
    return raw_data

def start_tests(args, config, AppTest_Instance): 
    '''
        Loads lmod data, custom yaml configs and calls submit_job() for the module(s) to be tested
    '''
    # Reading module list from spider  
    # lmod = get_raw_json(args)

    '''Alternate way to read lmod data, make sure to refresh the file with latest data first'''
    with open("/apps/apptests/lmod_spider_output.txt") as fh:
        lmod = json.load(fh)
        print("Warning: Using lmod data from lmod_spider_output.txt which might be outdated")
    
    # Reading test configurations from tests_config.yaml
    with open(config['TEST_CONFIG'], "r") as stream:
        try:
            yaml_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.debug(exc)
            print("YAML yaml_config file error. Please check the file.")

    # Tests all versions of the specified modules
    if(args.module):
        for module in args.module:    
            logger.debug(module)      
            dispatcher.submit_job(AppTest_Instance, config, lmod, yaml_config, module)
    
    # Tests a specific module/version 
    if(args.moduleversion):
        for arg in args.moduleversion:
            logger.debug(arg) 
            dispatcher.submit_job(AppTest_Instance, config, lmod, yaml_config, arg.split('/')[0], arg)
    
    if(args.testall):
        dispatcher.submit_all_jobs(AppTest_Instance, lmod, yaml_config)
        
    logger.debug("start_tests Done")

    # Tests running via SLURM now monitor status
    status.check_job_status(args, config, AppTest_Instance)