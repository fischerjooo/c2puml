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
    name="c_to_plantuml",
    version="1.1.0",
    description="Convert C/C++ code to PlantUML diagrams with high-performance parsing",
    long_description=open("README.md", "r", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="C to PlantUML Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "c2plantuml=c_to_plantuml.main:main",
            "c2plantuml-analyze=c_to_plantuml.main:c2plantuml_analyze",
            "c2plantuml-generate=c_to_plantuml.main:c2plantuml_generate",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Markup",
    ],
    keywords="c cpp plantuml diagram visualization code-analysis parsing",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/c_to_plantuml/issues",
        "Source": "https://github.com/yourusername/c_to_plantuml",
    },
)