#!/usr/bin/env python3
"""
Setup script for C to PlantUML Converter
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="c-to-plantuml",
    version="2.0.0",
    author="C to PlantUML Team",
    author_email="team@c-to-plantuml.com",
    description="Convert C/C++ code to PlantUML diagrams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/c-to-plantuml/converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "c2plantuml=c_to_plantuml.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)