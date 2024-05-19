import setuptools
import os
import io

NAME = "openfdm"
VERSION = "0.0.1.dev0"
DESCRIPTION = "openFDM is a Python package for Flight Data Monitoring (FDM)/Flight Operations Quality Assurance (FOQA)."
EMAIL = "coelho@ita.br"
AUTHOR = "Lucas Coelho e Silva"
REQUIRES_PYTHON = ">=3.10.4"
LICENSE = "MIT"

package_root = os.path.abspath(os.path.dirname(__file__))
readme_filename = os.path.join(package_root, "README.md")

with open(readme_filename, "r") as fh:
    long_description = fh.read()

# requirements
try:
    with io.open(os.path.join(package_root, "requirements.txt"), encoding="utf-8") as f:
        REQUIRED = f.read().splitlines()
except FileNotFoundError:
    REQUIRED = []


setuptools.setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=LICENSE,
    packages=setuptools.find_packages(),
    install_requires=REQUIRED,
    keywordsList=["anomaly detection", "anomaly", "flight"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=REQUIRES_PYTHON,
    include_package_data=True,
)
