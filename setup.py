"""minimal package setup"""

from setuptools import setup, find_packages

setup(
    name="geomag-wdc-web-app-interface",
    version="1.0.5",
    description="Retrieve geomagnetic observatory data via WDC and INTERMAGNET web services",
    author="L. Billingham",
    maintainer="W. Brown",
    maintainer_email="wb@bgs.ac.uk",
    license="MIT",
    keywords=["geomagnetism", "geomagnetic observatory data", "wdc", "intermagnet"],
    url="https://github.com/willjbrown88/geomag_wdc_web_app_interface",
    download_url="https://github.com/willjbrown88/geomag_wdc_web_app_interface/archive/1.0.5.tar.gz",
    
    python_requires=">=3.4",
    
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ["*.ini"]},
    zip_safe=False,
    install_requires=['requests==2.12.4',
                      'setuptools==27.2.0',
                      'six==1.10.0',
                      'sphinx==1.5.1'],
    extras_require={'develop': ['ipython==5.1.0',
                                'flake8==3.3.0',
                                'pylint==1.6.4',
                                'pytest==3.0.5',
                                'pytest-cov==2.3.1',
                                'sphinx==1.5.1']},
)
