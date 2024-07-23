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
        <li><a href="#creating-rcapptests.sh">Creating rcapptests.sh</a></li>
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
rcapptests stands for Research Computing Application Tests. This tool uses an environment modules
system (Lmod is currently supported) to generate a list of all environment modules on a computing
cluster and runs scheduled jobs on the same cluster to regularly test installed applications. A
collection of test/example data and standardized job scripts is needed to run the tests.

## Architecture


# Testing Applications on HiPerGator Cluster
## Creating rcapptests.sh
## Usage


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
- Fork [rcapptests](https://github.com/UFResearchComputing/rcapptests>).
- Inorder to start running locally you should setup:
    - A conda environemt (preferrable in /blue)
    - A development directory
 ### Step 1: Conda environment
 - Create a path based conda environment with python ```conda create -p <path> python=3.10```.
 - Activate the environment.
 - Install any packages required in this environment.

 ### Step 2: Development Directory
- In order to run rcapptests, fork [rcapptests](https://github.com/UFResearchComputing/rcapptests).
- Initializa an empty repository (git init) and then pull your forked repository (preferrably into /blue).
- This is your working directory.

### Step3: Running rcapptests locally
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
- Install the distribution with```python3 -m pip install dist/*.whl```.
- This step should install rcapptests inside your conda environment.
- NExt, copy ```/apps/rcapptests/bin/rcapptests``` into <your_conda_env_path>/bin/rcapptests.
- Modify the shebang (line 1 in the file) to point to <your_conda_env_path>/bin/python3.10.
- Run ```<your_conda_env_path>/bin/rcapptests``` and you are set.

Make changes, run apptests locally and test thoroughly. Create feature branches in your forked repository and raise PRs when ready.

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
- Install the distribution ```python3 -m pip install /apps/rcapptests/dev/*.whl```.

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
  

