#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2024 UFIT Research Computing
#
# Distributed under terms of the MIT license.

"""
Generate version automatically.
"""

import datetime
from setuptools import setup


def long_now_version():
    now = datetime.datetime.now()
    version = now.strftime("%y") + "." + now.strftime("%-m.%-d")
    return version

setup(
    use_calver=long_now_version,
)
