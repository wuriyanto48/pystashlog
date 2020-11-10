#!/usr/bin/env python

from setuptools import setup, find_packages
import pystashlog
import pathlib

HERE = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (HERE / 'README.md').read_text(encoding='utf-8')

setup(
    name='pystashlog', 
    version=pystashlog.__version__,
    description='Logstash client library for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wuriyanto48/pystashlog',
    author='wuriyanto',
    author_email='wuriyanto48@yahoo.co.id',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='logstash, elk, elastic, logstash client, kibana',
    packages=find_packages(exclude=['tests*', 'env', 'elk', '_examples']),
    python_requires='>=3.5',
    project_urls={
        'Bug Reports': 'https://github.com/wuriyanto48/pystashlog/issues',
        'Source': 'https://github.com/wuriyanto48/pystashlog/',
    },
)