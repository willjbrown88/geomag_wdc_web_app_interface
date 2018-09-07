"""minimal package setup"""

import os
from setuptools import setup, find_packages

# Allow us to read the README file
def readme(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Recursively include test data in package_data
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths

extra_files = package_files('gmdata_webinterface/tests/test_data')

setup(
    name="gmdata_webinterface",
    version="1.0.8",

    description="Retrieve geomagnetic observatory data via web services",
    long_description=readme("README.md"),

    author="L. Billingham",
    maintainer="W. Brown",
    maintainer_email="wb@bgs.ac.uk",

    license="MIT",

    keywords=["geomagnetism", "geomagnetic observatory data", "wdc", "intermagnet"],
    classifiers=["Programming Language :: Python :: 3"],

    url="https://github.com/willjbrown88/geomag_wdc_web_app_interface",

    python_requires=">=3.4",
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["*.ini"],
                  "": extra_files},
    zip_safe=False,
    install_requires=["requests>=2.12.4, <3.0",
                      "setuptools>=27.2.0",
                      "six>=1.10.0, <2.0",
                      "sphinx>=1.5.1, <2.0"],
    extras_require={"develop": ["ipython==5.1.0",
                                "flake8==3.3.0",
                                "pylint==1.6.4",
                                "pytest==3.0.5",
                                "pytest-cov==2.3.1",
                                "sphinx==1.5.1"]},
)

