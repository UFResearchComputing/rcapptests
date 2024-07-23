# rcapptests

rcapptests stands for Research Computing Application Tests. This tool uses an environment modules
system (Lmod is currently supported) to generate a list of all environment modules on a computing
cluster and runs scheduled jobs on the same cluster to regularly test installed applications. A
collection of test/example data and standardized job scripts is needed to run the tests.

# Contribution Guide
This is an open source package and contributions are welcome. Please follow the steps to contribute:
1) Fork rcapptests<https://github.com/UFResearchComputing/rcapptests>.
2) Create feature branches in your forked repository and create PRs when ready.

# Development Guide for HiPerGator Users
- This project is packaged using Setuptools backend and has the following directory structure:
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
- In order to run rcapptests, fork [rcapptests](https://github.com/UFResearchComputing/rcapptests), initializa an empty repository (git init) and then pull your forked repository (preferrably into /blue).
- In a seperate location from where you pulled rcapptests, create a conda environment from the ```requirements.txt``` file and activate it.

# Deploying rcapptests on HiPerGator Cluster
This guide is for deploying rcapptests on HiPerGator (/apps/rcapptests/) after any new changes. Make sure that you have tested locally and are good to deploy.
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
- Make sure you are in the apps group.
- Copy the dist/ folder into a dev folder i.e. ***/apps/rcapptests/dev/***.
- Activate the conda environment, ```conda activate /apps/rcapptests``` and then install the distribution ```python3 -m pip install /apps/rcapptests/dev/*.whl```.
- Note: If you installed any packages into your local conda environment, they must be added to dependencies inside your pyproject.toml.
- Any changes in configuration must be done in ```/apps/rcapptests/config.toml``` and the lua file for rcapptests.
- Test by running ```rcapptests```.
- If a rollback is required, install the distribution ```python3 -m pip install /apps/rcapptests/dist/*.whl``` else copy ```/apps/rcapptests/dev/``` into ```/apps/rcapptests/dist/```.

