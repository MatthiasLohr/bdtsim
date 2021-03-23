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
        'ecdsa==0.16.1',
        # TODO remove, see #43
        'eth-bloom @ git+https://github.com/konradkonrad/eth-bloom@update_eth_hash_dependency#egg=eth-bloom-1.0.3',
        'eth-tester==0.5.0b3',
        'graphviz==0.16',
        'hexbytes==0.2.1',
        'Jinja2==2.11.3',
        'py-evm==0.3.0a20',
        'py-solc-x==1.1.0',
        'PyYAML==5.4.1',
        'web3==5.17.0'
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
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Solidity',
        'Topic :: Scientific/Engineering',
    ],
    project_urls={
        'Documentation': 'https://bdtsim.readthedocs.io/',
        'Source': 'https://gitlab.com/MatthiasLohr/bdtsim',
        'Tracker': 'https://gitlab.com/MatthiasLohr/bdtsim/issues'
    }
)
