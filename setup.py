#!/usr/bin/env python
"""Setup script for the zerospeech2020 Python package"""

import codecs
import setuptools
import zerospeech2020

setuptools.setup(
    # general description
    name='zerospeech2020',
    description="Evaluation and validation tools for ZeroSpeech2020",
    version=zerospeech2020.__version__,

    # python package dependencies
    install_requires=['numpy', 'pyyaml'],
    setup_requires=[],

    # include Python code and any file in zerospeech2020/share
    packages=setuptools.find_packages(),
    package_data={'zerospeech2020': ['share/*']},
    zip_safe=True,

    # the command-line scripts to export
    entry_points={'console_scripts': [
        'zerospeech2020-validate = zerospeech2020.validation.main:main']},

    # metadata
    author='CoML team',
    author_email='zerospeech2020@gmail.com',
    license='GPL3',
    url='https://zerospeech.com/2020',
    long_description=codecs.open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
)
