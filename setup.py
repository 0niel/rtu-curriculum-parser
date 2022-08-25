from os.path import dirname, join

from setuptools import find_packages, setup

setup(
    name="curriculum_parser",
    version="1.0.0",
    packages=find_packages(),
    long_description=open(join(dirname(__file__), "README.txt")).read(),
)
