import os
from loguru import logger 
import subprocess

from rcapptests.test_handler.test import Test
from rcapptests.job_handler import trap_handler

def submit_all_jobs(AppTest_Instance, lmod, yaml_config):
    for module in lmod:
    # submit_job(lmod, yaml_config, module)
        pass


def submit_job(AppTest_Instance, config,  lmod, yaml_config, module, _module_version = None):
    '''
        Submits slurm jobs for valid modules provided
    '''
    logger.debug(_module_version)

    # Check if valid module name
    if module not in lmod.keys() :
        print("Error: Invalid module '" + module + "'")
        print("Warning: Maybe you have entered '<module>/<version>' with a '-m' flag. Use '-mv' instead.")
        # Mark the test as invalid
        AppTest_Instance.add_test(Test.invalid_test(module))
        return

    # Check if valid module/version
    if _module_version is not None :
        module_version = [(module, luaPath) for module in lmod for luaPath in lmod[module] if _module_version == lmod[module][luaPath]['fullName']]
        logger.debug(module_version)
        if len(module_version) == 0 :
            print("Error: Invalid version '" + _module_version + "'")
            print("Warning: Maybe you have entered '<module>' with a '-mv' flag. Use '-m' instead.")
            # Mark the test as invalid
            AppTest_Instance.add_test(Test.invalid_test(_module_version))
            return

    logger.debug("Valid module or module/version " + str(_module_version))

    # Parse lmod dict for dependency details
    for luaPath in lmod[module]:
        module_version = lmod[module][luaPath]["fullName"]
        logger.debug(module_version)
        if(_module_version is None or module_version == _module_version):
            test_file_path = os.path.join(config['TEST_PATH'], module, "rcapptests.sh")

            # Arguments to the sbatch command
            args = []
            dependencies = "-"

            # Check if custom test config (in tests_config.yaml) has been provided and parse it
            if(module_version in yaml_config.keys()):
                test_file_path = yaml_config[module_version]["path"]
                print("Info: Using custom file path " + test_file_path +" for " + module_version)
                if("args" in yaml_config[module_version]):
                    for arg in yaml_config[module_version]["args"].split(' '):
                        args.append(arg)
                    print("Info: Using custom dependency " + str(args) + " for " + module_version)
                    dependencies = "Custom config"

            logger.debug(test_file_path)

            # Add all dependencies to args if not in test config
            if len(args) == 0 and "parentAA" in lmod[module][luaPath]:
                for dependency in lmod[module][luaPath]["parentAA"][0]:
                    if(len(dependencies) == 1):
                        dependencies = dependency
                    else :
                        dependencies += "," + dependency
                    args.append(dependency)
                    
            logger.debug(dependencies)

            # Submit test job
            if(os.path.exists(test_file_path) and os.access(test_file_path, os.R_OK)):
                # Setting trap conditions and module loads in the test files
                newPath = trap_handler.addTrap(config, test_file_path)

                cmd = ['sbatch', newPath]

                args.append(module_version)
                cmd.extend(args)
                logger.debug(cmd)
                with subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                ) as proc:
                    res_stdout = proc.stdout.read()
                    res_stderr = proc.stderr.read()
                logger.debug(res_stdout)
                logger.debug(res_stderr)
                logger.debug("EXIT Code: {}".format(proc.returncode))

                # Add the current job to the RUNNING_TESTS list
                AppTest_Instance.add_test(Test.new_test(module_version, dependencies, os.path.join(module, "rcapptests.sh"), proc, res_stdout, res_stderr))
            else:
                print("Error: Cannot open or missing test file " + test_file_path)
                AppTest_Instance.add_test(Test.missing_test(module_version, dependencies, test_file_path))
