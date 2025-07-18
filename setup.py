#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="c-to-plantuml",
    version="2.0.0",
    author="C to PlantUML Contributors",
    author_email="contributors@example.com",
    description="A robust Python tool for converting C/C++ projects into comprehensive PlantUML diagrams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/c-to-plantuml",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "flake8>=3.9.0",
            "black>=21.0.0",
            "mypy>=0.900",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.12.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "c2plantuml=c_to_plantuml.main_optimized:main",
            "c2plantuml-analyze=c_to_plantuml.main_optimized:analyze_project_cli",
            "c2plantuml-generate=c_to_plantuml.main_optimized:generate_plantuml_cli",
        ],
    },
    include_package_data=True,
    package_data={
        "c_to_plantuml": ["*.json"],
        "tests": ["test_files/*.c", "test_files/*.h"],
    },
    zip_safe=False,
)