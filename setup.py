from setuptools import find_packages, setup

with open("PACKAGE.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="membrane-client",
    version="0.1",
    packages=find_packages(include=["membrane", "membrane.*"]),
    install_requires=["Flask>=2.3.1", "Flask-Login>=0.6.2", "PyJWT>=2.8.0"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
