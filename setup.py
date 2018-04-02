"""minimal package setup"""

from setuptools import setup, find_packages

requirements = [i.strip() for i in open("requirements.txt").readlines()]
dev_requirements = [
    i.strip() for i in open("requirements_dev.txt").readlines()
]
setup(
    name="geomag-wdc-web-app-interface",
    version="1.0.1",
    description="Retrieve geomagnetic observatory data via WDC and INTERMAGNET web services",
    author="L. Billingham",
    maintainer="W. Brown",
    maintainer_email="wb@bgs.ac.uk",
    license="MIT",
    keywords=["geomagnetism", "geomagnetic observatory data", "wdc", "intermagnet"],
    url="https://github.com/willjbrown88/geomag_wdc_web_app_interface",
    download_url="https://github.com/willjbrown88/geomag_wdc_web_app_interface/archive/1.0.1.tar.gz",
    
    python_requires=">=3.4",
    
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ["*.ini"]},
    zip_safe=False,
    install_requires=requirements,
    extras_require={'develop': dev_requirements}
)
