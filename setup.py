#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='foiegras',
      version='0.1',
      url='https://github.com/codeinthehole/foiegras',
      author="David Winterbottom",
      author_email="david.winterbottom@tangentlabs.co.uk",
      description="The missing CSV loading library for Postgres",
      long_description=open('README.md').read(),
      packages=find_packages())
