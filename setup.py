#!/usr/bin/env python

"""
AxiSurface: Simple Python 2/3 module to make line SVG files for plotting
"""

import os
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

doc_axisurface = __doc__.split('\n')

setup(
    name='AxiSurface',
    version='0.1.0',
    author='Patricio Gonzalez Vivo',
    author_email='patriciogonzalezvivo@gmail.com',
    description=doc_axisurface[0],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/patriciogonzalezvivo/AxiSurface',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'AxiSurface': ['*.py'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
    install_requires=requirements,
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'flake8', 'black'],
        'docs': ['sphinx', 'sphinx-rtd-theme'],
    },
    keywords='plotting, svg, gcode, axidraw, vector, graphics',
    project_urls={
        'Bug Reports': 'https://github.com/patriciogonzalezvivo/AxiSurface/issues',
        'Source': 'https://github.com/patriciogonzalezvivo/AxiSurface',
        'Documentation': 'https://github.com/patriciogonzalezvivo/AxiSurface#readme',
    },
    zip_safe=False,
)