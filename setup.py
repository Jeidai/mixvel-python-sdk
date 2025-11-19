# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
import os
import sys

if sys.version_info[0] < 3:
    from io import open

here = os.path.abspath(os.path.dirname(__file__))

packages = find_packages(where="src")

requires = [
    "httpx>=0.27",
    "pydantic>=2.8",
    "pydantic-xml>=2.7",
]

test_requirements = [
    "pytest>=8.2",
]

about = {}
with open(os.path.join(here, "src/mixvel", "__version__.py"), encoding="utf-8") as f:
    exec(f.read(), about)

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=packages,
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requires,
    python_requires=">=3.8",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    extras_require={
        "test": test_requirements,
    },
)
