
from setuptools import setup, find_packages


setup(
    name='CLImail',
    version='1.0',
    license='MIT',
    author="HRLO77",
    author_email='shakebmohammad.10@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/HRLO77/CLImail',
    description='A Command Line Interface email client written in python.',)
