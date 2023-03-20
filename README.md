# Traceback handler

Module to notify user of errors in all scripts, even when they run without terminal
* Traceback message in extended and easily readably format
* Open message in new terminal tab if script is running without terminal
* Developed for Linux OS where konsole application is available

## Installation

```shell
pip install git+https://github.com/quintenroets/tbhandler
```

This will create a new sitecustomize file and overwrite existing ones.
Alternatively, you can use the manual installation of the tbhandler in each of your scripts.

```shell
import tbhandler
tbhandler.install()
```
