from setuptools import setup, find_packages
import sys

requirements = [
    "owslib",
]
if sys.version_info.major == 2 and sys.version_info.minor < 7:
    requirements.append("argparse")
    
setup(
    name='ckanext-csw',
    version='0.2',
    author='Open Knowledge Foundation',
    author_email='okfn-dev@lists.okfn.org',
    license='AGPL',
    url='http://ckan.org/wiki/csw',
    description='CKAN official extensions',
    keywords='data packaging csw geodata catalogue',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    package_data={'ckan': ['i18n/*/LC_MESSAGES/*.mo']},
    entry_points="""
    [console_scripts]
    cswinfo = ckanext.csw.command:cswinfo
    """,
    test_suite = 'nose.collector',
)
