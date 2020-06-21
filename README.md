# treecode
[![Build Status](https://travis-ci.com/cmackenzie1/treecode.svg?branch=master)](https://travis-ci.com/cmackenzie1/treecode) [![](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)

A small python script the takes in an image of a [tentree](https://www.tentree.com/) treecode token and outputs
what it thinks the code is.

## Installation

- Clone the repository
- [Configure AWS Credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- Install the requirements
```bash
pip install -r requirements.dev.txt
```

## Usage

CLI
```bash
python -m treecode -i data/single/GYQ6JENN.jpeg
# Output
Detected Treecodes:
        - GYQ6JENN
```

Code
```python
from treecode import Client

client = Client()
with open("img.jpeg", "rb") as f:
    treecodes = client.treecode(f.read())
print(treecodes)
```