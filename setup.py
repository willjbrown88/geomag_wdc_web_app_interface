"""minimal package setup"""

from setuptools import setup, find_packages

requirements = [i.strip() for i in open("requirements.txt").readlines()]
dev_requirements = [
    i.strip() for i in open("requirements_dev.txt").readlines()
]
setup(
    name="geomag-webapp-interface",
    version="1.0.0",
    description="Retrieve geomagnetic observatory data via WDC and INTERMAGNET web services",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ["*.ini"]},
    zip_safe=False,
    install_requires=requirements,
    extras_require={'develop': dev_requirements}
)
