from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="membrane-backend",
    version="0.1",
    packages=find_packages(include=["membrane"]),
    install_requires=[],
)
