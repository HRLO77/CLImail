from setuptools import find_packages, setup
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CLImail",
    version="2.1.4",
    author="HRLO77",
    license='MIT',
    author_email="shakebmohammad.10@gmail.com",
    description="A Command Line Interface email client written in python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HRLO77/CLImail",
    packages=setuptools.find_packages()+['CLImail'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)