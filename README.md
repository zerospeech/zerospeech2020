# ZeroSpeech Challenge 2020 Python package

This repository bundles all the scripts required to evaluate and validate a
submission to the [ZeroSpeech Challenge 2020](https://zerospeech.com/2020).

## Installation

This installation is working on Linux and MacOS systems with
[conda](https://docs.conda.io/en/latest/miniconda.html) installed.

Create a new conda environment with required dependencies, clone the source code
and install it:

    git clone git@github.com:bootphon/zerospeech2020.git
    cd zerospeech2020
    conda env create -n zerospeech2020 -f environment.yaml
    conda activate zerospeech2020
    python setup.py install


## Usage

To use the program, do not forget to activate its virtual environment::

    conda activate zerospeech2020

The `zerospeech2020` program provides 2 command-line tools:

* `zerospeech2020-validate` which validates a submission, ensuring all the
  required files are here and correctly formatted.

* `zerospeech2020-evaluate` which evaluates a submission (supposed valid). Only
  the development datasets are evaluated. the surprise datasets can only be
  evaluated by doing an official submission to the challenge.

Each tool comes with a `--help` option describing the possible arguments (e.g.
`zerospeech2020-validate --help`).

More information at https://zerospeech.com/2020/instructions.html#validation and
https://zerospeech.com/2020/instructions.html#evaluation.
