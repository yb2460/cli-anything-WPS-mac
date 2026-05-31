# -*- coding: utf-8 -*-
"""CLI-Anything Photoshop Harness — 通过 COM 自动化操控 Adobe Photoshop。"""
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-photoshop",
    version="1.0.0",
    description="CLI harness for Adobe Photoshop via COM automation",
    author="cli-anything contributors",
    python_requires=">=3.10",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    package_data={
        "cli_anything.photoshop": ["skills/*.md"],
    },
    install_requires=[
        "click>=8.0",
        "pywin32>=305",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-photoshop=cli_anything.photoshop.photoshop_cli:main",
        ],
    },
)
