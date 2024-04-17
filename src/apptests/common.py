#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2024 UFIT Research Computing
#
# Distributed under terms of the MIT license.

"""
Set up logging and configuration.
"""

import logging
import os
import sys
import tomli
from loguru import logger
from pathlib import Path


def _setup_logging(debug=False, verbose=False, logfile=None):
    """Set the correct logging level and logger sinks."""
    global logger
    logger.remove()
    global DEBUG
    DEBUG = False
    global VERBOSE
    VERBOSE = False
    if verbose:
        VERBOSE = True
    if debug:
        DEBUG = True
        VERBOSE = True
    else:
        DEBUG = False
    if verbose:
        level = logging.INFO
    else:
        level = logging.WARN
    if debug:
        level = logging.DEBUG
        logger.add(sys.stderr, level=level)
        logger.debug("Debugging output enabled")
        if logfile:
            logger.debug("Logging to {}", logfile)
    else:
        logger.add(sys.stderr, level=level)
        if logfile:
            logger.info("Logging to {}", logfile)
    if logfile:
        logger.add(logfile, level=level)
    logger.debug("Logging level set to : {}", level)
    return logger


def _get_config(args, config_file=None, config_filename=None, config_var=None):
    """
    Retrieve site-specific lustre filesystem configurations from a config file. Follow a layered
    approach - config is retrieved in order from a toml config file specified either as a cli
    argument, RCAPPSTESTS_CONF env var, from the current directory, ~/.config/rc, or $RCDIR/conf.
    """
    if config_file:
        logger.debug(f"Retrieving config from specified {config_file}")
    else:
        config_type, config_file = _get_config_path(config_filename, config_var)
        logger.debug(f"Retrieving config from {config_type}: {config_file}")
    if not config_file:
        logger.error("No configuration file specified or found in the default paths. Exiting.")
        sys.exit(1)
    with open(config_file, "rb") as fh:
        config = tomli.load(fh)
    logger.debug(f"Config: {config}")
    return config


def _check_path(config_type, config_path):
    """Check if a path exists and is readable."""
    try:
        if config_path.exists():
            logger.debug(f"Using {config_path} from {config_type}")
            return True
        else:
            logger.debug(
                f"{config_path}, specified in {config_type}, does not exist or is not readable.")
    except PermissionError as e:
        logger.debug(f"Permission error for {config_path}, {e}")
        return False


def _get_config_path(config_filename=None, config_var=None, personal_rcdir=None):
    """
    Get the path to the config file.
    Hierarchy:
        * env variable
        * config file in the current directory
        * config file in the ~/.config/rc/ directory
        * config file in the $RCDIR/conf/ directory
    """
    if not config_filename and not config_var:
        return None
    config_env_path = os.getenv(config_var, None)
    if config_env_path:
        config_type = "env"
        config_path = Path(config_env_path)
        if _check_path(config_type, config_path):
            return config_type, str(config_path)
    # Check curdir next
    config_type = "curdir"
    config_path = Path.cwd() / Path(config_filename)
    if _check_path(config_type, config_path):
        return config_type, str(config_path)
    # Check $HOME/.config/ufrc next
    config_type = "home"
    config_path = Path.home() / ".config/rc" / Path(config_filename)
    if _check_path(config_type, config_path):
        return config_type, str(config_path)
    # Finally, check the RCDIR for a canonical config file
    config_type = "rcdir"
    config_path = Path(_get_rcdir(personal_rcdir), "conf", config_filename)
    if _check_path(config_type, config_path):
        return config_type, str(config_path)
    return None, None


def _get_rcdir(personal_rcdir):
    """
    Parse rccms configuration file and return the config object.
    """
    rcdir = ""
    env_rcdir = os.getenv("RCDIR", None)
    if env_rcdir:
        logger.debug(f"RCDIR from env: {env_rcdir}")
        rcdir = env_rcdir
#    elif args.rcdir:
#        logger.debug(f"RCDIR from args: {args.rcdir}")
#        rcdir = args.rcdir
    elif personal_rcdir:
        if os.path.exists(personal_rcdir):
            rcdir = personal_rcdir
    else:
        rcdir = '/apps/rc'
        logger.debug(f"RCDIR set to the default path {rcdir}")
    return rcdir
