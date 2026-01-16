"""
Setup configuration for docassemble-dag package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="docassemble-dag",
    version="0.3.0",
    description="Static analyzer for extracting explicit dependency graphs from Docassemble YAML interviews",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="",
    url="",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "pyyaml>=5.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "docassemble-dag=docassemble_dag.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
