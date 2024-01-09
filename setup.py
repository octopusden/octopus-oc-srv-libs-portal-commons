#! /usr/bin/env python
import glob
import os
import sys

from setuptools import setup
from setuptools import find_packages

__version = "11.0.5"

def list_recursive(app, directory, extension="*"):
    """
    it's the only way to include dir recursively
    MANIFEST file can be used but is does not includes to binary distribution 
    """
    dir_to_walk = os.path.join(app, directory)
    found = [result for (cur_dir, subdirs, files) in os.walk(dir_to_walk)
             for result in glob.glob(os.path.join(cur_dir, '*.' + extension))]
    found_in_package = map(lambda x: x.replace(app + "/", "", 1), found)
    return list (found_in_package)


included_packages = find_packages()

# notes:
# 1. "mock" is a part of Python "unittest" (comes with interpreter since 3.6), removed from dependencies
# 2. Python 2.7 is now obsolete since "oc-delivery-apps" has no support for it (comes from Django 3)

spec = {
        "name": "oc-portal-commons",
        "version": __version,
        "description": "Common code, static files, settings and testing tools used at all portal variants",
        "long_description": "",
        "long_description_content_type": "text/plain",
        "install_requires": [
            "oc-delivery-apps >=  11.2.8",
            "packaging",
            "pyparsing == 2.4.0",
            "django-jquery",
            "django-tests",
            "django-filter",
            "fs"],
        "packages": included_packages,
        "package_data": {
            "oc_portal_commons": list_recursive("oc_portal_commons", "templates")
                             + list_recursive("oc_portal_commons", "static")},
        "python_requires": ">=3.6"}

setup(**spec)
