"""minimal package setup"""

from setuptools import setup, find_packages

requirements = [i.strip() for i in open("requirements.txt").readlines()]
dev_requirements = [
    i.strip() for i in open("requirements_dev.txt").readlines()
]
setup(
    name="geomag-webapp-interface",
    version="0.1.0",
    description="retrieve geomagnetic observatory data via WDC and INTERMAGNET web services",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements
)
