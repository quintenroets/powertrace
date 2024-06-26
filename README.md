# Powertrace
[![PyPI version](https://badge.fury.io/py/powertrace.svg)](https://badge.fury.io/py/powertrace)
![Python version](https://img.shields.io/badge/python-3.10+-brightgreen)
![Operating system](https://img.shields.io/badge/os-linux%20%7c%20macOS-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)


Detailed stack trace logging and visualization.
* Rich traceback visualization
* Also works for headless scripts
* Easy to reproduce visualization

## Usage

Run
```python
import powertrace

powertrace.visualize_traceback()
```
To visualize the current traceback.

Run
```python
import powertrace

powertrace.install_traceback_hooks()
```
In the beginning of your script to enable advanced traceback handling.

## Installation
```shell
pip install powertrace
```

or

```shell
pip install powertrace-hooks
```
to enable advanced traceback handling in all scripts without having to run

```python
import powertrace

powertrace.install_traceback_hooks()
```

at the start of every script.
