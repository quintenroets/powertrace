# Powertrace
[![PyPI version](https://badge.fury.io/py/powertrace.svg)](https://badge.fury.io/py/powertrace)
![PyPI downloads](https://img.shields.io/pypi/dm/powertrace)
![Python version](https://img.shields.io/badge/python-3.11+-brightgreen)
![Operating system](https://img.shields.io/badge/os-linux%20%7c%20macOS-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

Improved rich tracebacks:
* Handles exceptions in threads
* Includes failed subprocess output
* Can be auto-enabled in every Python process
* Imports nothing until an exception occurs: over 100x less startup overhead than rich's own hook

![example](https://github.com/quintenroets/powertrace/blob/main/assets/examples/visualization.png?raw=true)

## Usage

```python
import powertrace

powertrace.install()
```
Call at the top of a script to render its uncaught exceptions.

```python
import powertrace

try:
    ...
except Exception:
    powertrace.show_exception()
```
Renders the exception being handled.

## Installation
```shell
pip install powertrace        # call install() yourself
pip install powertrace-hooks  # no need to call install()
```
