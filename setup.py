from setuptools import setup, find_packages
import sys

requirements = [
    "owslib",
    "lxml<=2.2.99",
]
if not sys.version.startswith("2.7") and not sys.version.startswith("3"):
    requirements.append("argparse")
    
setup(
    name='ckanext-csw',
    version='0.3',
    author='Open Knowledge Foundation',
    author_email='okfn-dev@lists.okfn.org',
    license='AGPL',
    url='http://ckan.org/wiki/csw',
    description='CKAN official extensions',
    keywords='data packaging csw geodata catalogue',
    #install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    entry_points="""
    [console_scripts]
    cswinfo = ckanext.csw.command:cswinfo

    [ckan.plugins]
    # Add plugins here, eg
    cswserver=ckanext.csw.plugin:CatalogueServiceWeb
    """,
    test_suite = 'nose.collector',
)
