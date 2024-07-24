# rcapptests

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#what-is-rcapptests">What is rcapptests</a>
      <ul>
        <li><a href="#architecture">Architecture</a></li>
      </ul>
    </li>
    <li>
      <a href="#testing-applications-on-hipergator-cluster">Testing Applications on HiPerGator Cluster</a>
      <ul>
        <li><a href="#rcapptestssh">rcapptests.sh</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
   <li>
    <a href="#development-guide">Development Guide</a>
    <ul>
      <li><a href="#project-structure">Project Structure</a></li>
      <li><a href="#contribution-guide-for-hipergator-cluster">Contributing</a></li>
      <li><a href="#deploying-rcapptests-on-hipergator-cluster">Deploying</a></li>
    </ul>
  </li>
    <li><a href="#license">License</a></li>
    <li><a href="#authors">Authors</a></li>
  
  </ol>
</details>

# What is rcapptests?
rcapptests stands for Research Computing Application Tests. It is a CLI tool uthat uses an environment modules
system (Lmod is currently supported) to generate a list of all environment modules on a computing
cluster and runs scheduled jobs on the same cluster to test installed applications. A
collection of test/example data and standardized job scripts are needed to run the tests.

## Architecture
The tool uses Lmod to identify all the applications installed on the cluster. Each application is expected to have test cases. 
rcapptests will schedule jobs on the cluster for all dependencies and all versions for each application. These jobs will invoke the test cases and report results. 

Let's use some terminologies to better understand the architecture:
- Invocation: An invocation refers to a specific application along with its version and dependencies. For example, if a cluster has python/3.6, python/3.7 and python/3.8 and each version also has gcc/12.2 dependency, then the resulting invocations are:
  
| Invocation | Application    | Dependencies |
|------------|----------------|--------------|
| 1          | python/3.6     | gcc/12.2     |
| 2          | python/3.6     | -            |
| 3          | python/3.7     | gcc/12.2     |
| 4          | python/3.7     | -            |
| 5          | python/3.8     | gcc/12.2     |
| 6          | python/3.8     | -            |

Therefore, it makes sense to test each invocation seperately. 

- Driver job (rcapptests.sh): The cluster should have test cases for each application. In order to run all those tests for each dependency and version, a driver script is needed. This script will load the correct version and dependencies, followed by running the actual tests via SLURM. On the HiPerGator cluster, test cases for each application are in ```/data/apps/tests/<app_name>```. Each application here should have an ```rcapptests.sh``` file before it can be tested with this tool on the cluster. 

![Untitled (1)](https://github.com/user-attachments/assets/b91ab816-feab-44df-aef0-45026d23b6c7)


# Testing Applications on HiPerGator Cluster
## 1) rcapptests.sh
From the previous section, it is clear that the ```rcapptests.sh``` file is central to the tool. Let's talk about it.

```sh
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=7000mb
#SBATCH --time=00:30:00
# The following line must be included:
#SBATCH --output=/data/apps/tests/rcapptests/slurm_logs/%j.log

echo 'Write any tests here'
date
hostname
python /data/apps/tests/python/test_simple.py
echo 'Test has completed'
```
rcapptests.sh is a standard slurm job script with the following properties:
- It has no 'module loads' or 'ml' commands.
- No email configured with ```#SBATCH --mail-user=<email_id>```. This is to avoid getting too many emails. 
- The output file should always be ```/data/apps/tests/rcapptests/slurm_logs/%j.log``` unless changed in the configuration and lua files. This output file will store the driver script logs.
- Always give full absolute paths, never relative paths. 

### Using an output directory to write test data: $APPTESTS_OUT_DIR
Some tests require a working/output directory to write the test specific data in ```/data/apps/tests/<app_name>```. For example, the cactus application on the HiPErGator cluster requires a working directory for every test. If tests are run for each invocation, then multiple such directories are needed. Following is the original ```rcapptests.sh``` driver script for cactus.

```sh
#!/bin/bash
#SBATCH --job-name=cactus_test
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=40gb
##SBATCH --partition=gpu
##SBATCH --gpus=a100:1
#SBATCH --time=24:00:00
#SBATCH --output=/data/apps/tests/rcapptests/slurm_logs/%j.log

date;hostname;pwd
echo "Setting up test environment..."
echo ${identifier}

TEST_PWD=/data/apps/tests/cactus
TEST_DATADIR=${TEST_PWD}/example_data
TEST_WORKDIR=${TEST_PWD}/output

cd ${TEST_PWD}

# Remove any previous test results and re-create a working directory
rm -rf ${TEST_WORKDIR}
mkdir -p ${TEST_WORKDIR}
#d ${TEST_WORKDIR}

echo "Starting test run at $(date) on $(hostname)..."

# export TOIL_SLURM_ARGS="--partition gpu --gpus=a100:1"
unset XDG_RUNTIME_DIR

################################################################################
# The "step-by-step" method below will produce a file with a list of cactus
# commands, each of which can be modified (if needed) and placed in its own
# separate job

cactus-prepare \
    ${TEST_DATADIR}/evolverMammals.txt \
    --jobStore ${TEST_WORKDIR}/jobstore \
    --outDir ${TEST_WORKDIR}/steps-output \
    --outHal ${TEST_WORKDIR}/steps-output/evolverMammals.hal \
    --outSeqFile ${TEST_WORKDIR}/steps-output/evolverMammals.txt \
    > ${TEST_WORKDIR}/steps.sh
#    --cactusOptions '--batchSystem single_machine --workDir /data/apps/tests/cactus/work --clean never --cleanWorkDir never' \
#    --gpu 1 \

# For testing the installation, the following command blindly runs the steps
# generated by cactus-prepare. In real life, the user would likely modify the
# "steps.sh" file options and break up the rounds into separate SLURM jobs.
#
/bin/bash ${TEST_WORKDIR}/steps.sh
################################################################################

echo "Test complete at $(date)."
```

In this script, we will change ```TEST_WORKDIR``` to ```TEST_WORKDIR=${TEST_PWD}/output/${APPTESTS_OUT_DIR}```. The resulting directory structure will be:

```
/data/apps/tests/cactus
├── *
└── output/
    └── APPTESTS_OUT_cactus/
        ├── 2.0.3/*
        └── 2.0.5/*
        └── 2.2.4/*
        └── 2.8.0/*
```
Now, the test specific data for the invocation of cactus/2.0.3 will be in ```/data/apps/tests/cactus/output/APPTESTS_OUT_cactus/2.0.3/*```. Further, inside each version there can be subdirs for different dependencies.

## 2) Usage
Once ```rcapptests.sh``` is setup, the application is ready to be tested. Load the rcapptests module with ``ml rcapptests``. 

```
$ rcapptests -h
usage: main.py [-h] [--version] [-m MODULE [MODULE ...]] [-mv MODULEVERSION [MODULEVERSION ...]] [-testall] [-v] [-o OUTPUT]

_______________________________________________________________
|                                                             |
|           Internal tool to run application tests            |
|                                                             |
|   How to test an application:                               |
|   1) Create a test script in /data/apps/test/<app> where    |
|      'app' is the application to be tested.                 |
|   2) Copy the driver script rcapptests.sh from /data/apps/  |
|      tests/rcapptests/rcapptests.sh. Modify the driver      |
|      script to include tests.                               |
|   3) Run the tests. (Eg: apptests -m <app>, apptests -mv    |
|      app/version etc)                                       |
|   4) Check the report and slurm_logs in /data/apps/test/    |
|      rcapptests/*, full paths will be shown once tests      |
|      complete.                                              |
|                                                             |
|   Note: Custom test script paths and dependencies can be    |
|   provided in HPC_APPTESTS_DIR/tests_config.yaml.           |
|                                                             |
|   usage=rcapptests [options] [group]                        |
|_____________________________________________________________|

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -m MODULE [MODULE ...], --module MODULE [MODULE ...]
                        MODULE should not include the version. Runs test for all versions(s) of the MODULE provided.
  -mv MODULEVERSION [MODULEVERSION ...], --moduleversion MODULEVERSION [MODULEVERSION ...]
                        MODULEVERSION: <module>/<version>. Runs test for the specific version of the module provided.
  -testall, --testall   Runs tests for all modules in the system.
  -v, --verbose         verbose output
  -o OUTPUT, --output OUTPUT
                        Output fields. Accepted fields are [Module,Dependency,TestFile,Time,JobId,SlurmLogs,JobStatus,TestStatus,ExitCode]
```

2) In order to test a python/3.10, the command ```rcapptests -mv python/3.10``` 

# Development Guide
## Project Structure
- This project has the following directory structure:
```
rcapptests /
├── LICENSE
├── pyproject.toml
├── README.md
|── AUTHORS.md
|── requirements.txt
└── src/
    └── rcapptests/
        ├── job_handler/*
        └── test_handler/*
        └── report_handler/*
        └── main.py
```

## Contribution Guide for HiPerGator Cluster
This is an open source package and contributions are welcome. Please follow the steps to contribute:
- In order to start running locally you should setup:
    - A conda environemt (preferrable in /blue)
    - A development directory
 ### Step 1: Conda environment
 - Create a path based conda environment with python ```conda create -p <path> python=3.10```.
 - Activate the environment.

 ### Step 2: Development Directory
- In order to run rcapptests, fork [rcapptests](https://github.com/UFResearchComputing/rcapptests).
- Initializa an empty repository (git init) and then pull your forked repository (preferrably into /blue).
- This is your working directory.

### Step 3: Running rcapptests locally
- Make sure the conda environment created in Step 1 is active.
- This project is packaged using [Setuptools](https://packaging.python.org/en/latest/key_projects/#setuptools) backend. To generate [distribution packages](https://packaging.python.org/glossary/#term-distribution-package) for the rcapptests package, run this command from the local directory where you have pyproject.toml:
```sh
python3 -m build
```
- This command should output a lot of text and once completed should generate two files in the dist directory:
```
dist/
├── rcapptests-<version>-py3-none-any.whl
└── rcapptests-<version>.tar.gz
```
- Install the distribution with ```python3 -m pip install /apps/rcapptests/dev/rcapptests-<your_version>-py3-none-any.whl```.
- This step should install rcapptests inside your conda environment.
- NExt, copy ```/apps/rcapptests/bin/rcapptests``` into <your_conda_env_path>/bin/rcapptests.
- Modify the shebang (line 1 in the file) to point to <your_conda_env_path>/bin/python3.10.
- Run ```<your_conda_env_path>/bin/rcapptests``` and you are set.

Make code changes, run apptests locally and test thoroughly. Create feature branches in your forked repository and raise PRs when ready.
If any python package(s) are required, add as [dependencies] under ```pyproject.toml``` and repeat step 3 for installing them.

## Deploying rcapptests on HiPerGator Cluster
This guide is for deploying rcapptests on HiPerGator (/apps/rcapptests/) after any new changes. 
- In a local directory, clone [rcapptests](https://github.com/UFResearchComputing/rcapptests>). This is your working directory.
- Activate the production conda environment, ```conda activate /apps/rcapptests```
- To generate [distribution packages](https://packaging.python.org/glossary/#term-distribution-package) for the rcapptests package, run this command from the local directory where you have pyproject.toml:
```sh
python3 -m build
```
- This command should output a lot of text and once completed should generate two files in the dist directory:
```
dist/
├── rcapptests-<version>-py3-none-any.whl
└── rcapptests-<version>.tar.gz
```
- Make sure you are in the apps group.
- Copy the dist/ folder into ***/apps/rcapptests/dev/***.
- Install the distribution ```python3 -m pip install /apps/rcapptests/dev/rcapptests-<your_version>-py3-none-any.whl```. If the version is already installed, use ```python3 -m pip install --force-reinstall /apps/rcapptests/dev/rcapptests-<your_version>-py3-none-any.whl``` to override pip cache.

***Note:***
```
- If you installed any packages into your local conda environment, they must be added to dependencies inside your pyproject.toml.
- Any changes in configuration must be done in /apps/rcapptests/config.toml and the lua file for rcapptests.
```
- Test by running ```rcapptests```.
- If a rollback is required, install the distribution ```python3 -m pip install /apps/rcapptests/dist/*.whl``` else copy ```/apps/rcapptests/dev/``` into ```/apps/rcapptests/dist/```.

# License 
UFResearchComputing/rcapptests is licensed under the [MIT License](https://github.com/UFResearchComputing/rcapptests/blob/main/LICENSE).

# Authors
- Sohaib Syed <sohaibuddinsyed@ufl.edu/syedsohaib074@gmail.com>
- Oleksandr Moskalenko <moskalenko@ufl.edu>
  

