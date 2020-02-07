# ZeroSpeech Challenge 2020 Python package

This repository bundles all the scripts required to evaluate and validatea
submission to the [ZeroSpeech Challenge 2020](https://zerospeech.com/2020).

## Installation

This installation is working on Linux and MacOS systems with
[conda](https://docs.conda.io/en/latest/miniconda.html) installed.


### From conda

The simplest way is using conda. The following command will install the package
in a newly created virtual environment named *zerospeech2020*::

    conda create -n zerospeech2020 -c coml zerospeech2020

Then, to use it, simply activate the virtual environment::

    conda activate zerospeech2020


### From source

Create a new conda environment with required dependencies, clone the source code
and install it::

    conda create -n zerospeech2020 -c coml python=3.7 tde=0.2 abx=0.4.3
    conda activate zerospeech2020
    git clone git@github.com:bootphon/zerospeech2020.git
    cd zerospeech2020
    python setup.py install


## Usage

`zerospeech2020` provides 2 command-line tools:

* `zerospeech2020-validate` which validates a submission, ensuring all the
  required files are here and correctly formatted.

* `zerospeech2020-evaluate` which evaluates a submission (supposed valid). Only
  the development datasets are evaluated. the surprise datasets can only be
  evaluated by doing an official submission to the challenge.

Each tool comes with a `--help` option describing the possible arguments (e.g.
`zerospeech2020-validate --help`).
