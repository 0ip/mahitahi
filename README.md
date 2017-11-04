<div align="center">
    <h1>PyCRDT</h1>
    <h5>a Python-based (sequence) CRDT library for collaborative text editing</h5>
</div>

<div align="center">
    <a href="https://travis-ci.org/0ip/pycrdt">
        <img src="https://img.shields.io/travis/0ip/pycrdt.svg?style=flat-square">
    </a>
    <a href='http://boilpy.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/pycrdt/badge/?style=flat-square&version=latest'/>
    </a>
</div>

_Status: WIP/Proof of concept_

This library relies on the ideas presentend in [Logoot](https://doi.org/10.1109%2FTPDS.2009.173) and [LSEQ](https://doi.org/10.1145%2F2494266.2494278).

See `examples/mqtt_gui.py` for an Etherpad-like clone realized with PyQt's `QPlainTextEdit` widget, MQTT as broadcast channel and _Fernet_ for encryption.

### Table of Contents
* [Installation](#installation)
* [Running tests](#tests)
* [License](#license)

#### Installation
Download or clone the repository using `git`:

```console
$ git clone https://github.com/0ip/pycrdt.git
```

#### Running tests

In order to run tests, make sure to have PyTests installed, then run

```console
$ PYTHONPATH=. pytest
```


#### License
This repository has been released under the [MIT License](LICENSE).