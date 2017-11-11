<div align="center">
    <h1>MahiTahi</h1>
    <h5>a Python-based (sequence) CRDT library for collaborative text editing</h5>
</div>

<div align="center">
    <a href="https://travis-ci.org/0ip/mahitahi">
        <img src="https://img.shields.io/travis/0ip/mahitahi.svg?style=flat-square">
    </a>
</div>

_Status: WIP/Proof of concept_

This library relies on the ideas presentend in [Logoot](https://doi.org/10.1109%2FTPDS.2009.173) and [LSEQ](https://doi.org/10.1145%2F2494266.2494278).

See `examples/mqtt_gui.py` for an Etherpad-like clone realized with PyQt's `QPlainTextEdit` widget, MQTT as broadcast channel and _Fernet_ for encryption.

### Table of Contents
* [Installation](#installation)
* [Usage](#usage)
* [Running tests](#tests)
* [License](#license)

#### Installation
Download or clone the repository using `git`:

```console
$ git clone https://github.com/0ip/mahitahi.git
```

#### Usage

```python
from mahitahi import Doc

init_doc = Doc()
init_doc.insert(0, "A")
init_doc.insert(1, "B")
init_doc.insert(2, "C")
init_doc.insert(3, "\n")

a_doc = deepcopy(init_doc)
a_doc.site = 1
patch_from_a = a_doc.insert(1, "x")

b_doc = deepcopy(init_doc)
b_doc.site = 2
patch_from_b = b_doc.delete(2)

a_doc.apply_patch(patch_from_b)

assert a_doc.text == "AxB\n"

b_doc.apply_patch(patch_from_a)

assert b_doc.text == "AxB\n"
```

#### Running tests

In order to run tests, make sure to have PyTests installed, then run

```console
$ PYTHONPATH=. pytest
```


#### License
This repository has been released under the [MIT License](LICENSE).