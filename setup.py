#! /usr/bin/env python2.7
import glob
import os
import sys

from setuptools import setup, find_packages
from datetime import datetime

__version="11.0.1"

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

setup(name="oc_portal_commons",
      version=__version,
      description="Common code, static files, settings and testing tools used at all portal variants",
      long_description="",
      long_description_content_type="text/plain",
      install_requires=[
          "oc-delivery-apps >= 11.2.8",
          "packaging",
          "pyparsing == 2.4.0",
          "django-jquery", 
          "django-tests",
          "django-filter",
          "fs",
          "mock"
      ],
      packages=included_packages,
      package_data={
          "oc_portal_commons": (list_recursive("oc_portal_commons", "templates")
                             + list_recursive("oc_portal_commons", "static")),
      },
      test_suite="oc_portal_commons.test.runtests.execute_test_suite",
      )
