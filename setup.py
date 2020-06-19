# This file is part of the Blockchain Data Trading Simulator
#    https://gitlab.com/MatthiasLohr/bdtsim
#
# Copyright 2020 Matthias Lohr <mail@mlohr.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='bdtsim',
    description='Blockchain Data Trading Simulator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author='Matthias Lohr',
    author_email='mail@mlohr.com',
    url='https://gitlab.com/MatthiasLohr/bdtsim',
    license='Apache License 2.0',
    install_requires=[
        'eth-tester==0.5.0b1',
        'graphviz==0.14',
        'hexbytes==0.2.0',
        'Jinja2==2.11.2',
        'py-evm==0.3.0a17',
        'py-solc-x==0.8.2',
        'PyYAML==5.3.1',
        'web3==5.11.1'
    ],
    python_requires='>=3.7.*, <4',
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={
        'bdtsim': ['*.sol']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bdtsim=bdtsim.cli.main:main'
        ]
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
    ],
    project_urls={
        'Documentation': 'https://matthiaslohr.gitlab.io/bdtsim/',
        'Source': 'https://gitlab.com/MatthiasLohr/bdtsim',
        'Tracker': 'https://gitlab.com/MatthiasLohr/bdtsim/issues'
    }
)
