#/usr/python
import subprocess
import shlex
import json
import os 

def get_raw_json():
    spider = "/apps/lmod/lmod/libexec/spider"
    modulepath_root = os.environ["MODULEPATH"]

    """Retrieve raw json data from either spider output or from a test file."""
    # log = args.log
    # Dev: /apps/lmod/dev/libexec/spider -o spider-json /apps/lmod/devmodulefiles
    cmd = "{} -o spider-json {}".format(spider, modulepath_root)
    # if args.debug:
        # log.debug("Cmd: '{}'".format(cmd))
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
        # if args.debug:
            # log.debug(res_stderr)
    # if args.debug and args.verbose:
    #     log.debug("stdout: '{}'".format(res_stdout))
    # if not res_stdout:
        # log.error("Error: No output from the spider command.")
    raw_data = json.loads(res_stdout)
    # if args.debug:
        # log.debug(raw_data)
    return raw_data