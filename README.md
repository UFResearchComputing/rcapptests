# rcapptests

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">What is rcapptests</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#dependencies">Dependencies</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contribution-guide-for-hipergator-users">Contributing</a></li>
    <li><a href="#deploying-rcapptests-on-hipergator-cluster">Deploying</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#authors">Authors</a></li>
  
  </ol>
</details>

rcapptests stands for Research Computing Application Tests. This tool uses an environment modules
system (Lmod is currently supported) to generate a list of all environment modules on a computing
cluster and runs scheduled jobs on the same cluster to regularly test installed applications. A
collection of test/example data and standardized job scripts is needed to run the tests.

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
- This project is packaged using Setuptools backend and has the following directory structure:
# Contribution Guide for HiPerGator Users
This is an open source package and contributions are welcome. Please follow the steps to contribute:
- Fork [rcapptests](https://github.com/UFResearchComputing/rcapptests>).
- Inorder to start running locally you should setup:
    - A conda environemt (preferrable in /blue)
    - A development directory
 ## Step 1: Conda environment
 - Create a path based conda environment with python ```conda create -p <path> python=3.10```.
 - Activate the environment.
 - Install any packages required in this environment.

 ## Step 2: Development Directory
- In order to run rcapptests, fork [rcapptests](https://github.com/UFResearchComputing/rcapptests).
- Initializa an empty repository (git init) and then pull your forked repository (preferrably into /blue).
- This is your working directory.

## Step3: Running rcapptests locally
- Make sure the conda environment created in Step 1 is active.
- Generate [distribution packages](https://packaging.python.org/glossary/#term-distribution-package) for the rcapptests package, run this command from the local directory where you have pyproject.toml:
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

# Deploying rcapptests on HiPerGator Cluster
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

  # Authors
  

