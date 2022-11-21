# aklog
Android developer's Swiss Army Knife for Log

### Installation

Run the following in your command-line:

```shell
$ brew tap wswenyue/aklog && brew install aklog
```

### Update

If you need to update，Run the command:

```shell
$ brew upgrade aklog
```

### How to use

```shell
$ aklog -h

usage: aklog.py [-h] [-v] [-t TAG] [-l LEVEL] [-m MSG]
                [-mj MSG_JSON_VALUE [MSG_JSON_VALUE ...]] [-p PACKAGE]
                [-pe PACKAGE_EXCLUDE [PACKAGE_EXCLUDE ...]] [-i] [-e] [-a]

Android developer's Swiss Army Knife for Log

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -t TAG, --tag TAG     Filter logs with tag
  -l LEVEL, --level LEVEL
                        Filter logs using log level (V,D,I,W,E)
  -m MSG, --msg MSG     Filter logs with msg
  -mj MSG_JSON_VALUE [MSG_JSON_VALUE ...], --msg_json_value MSG_JSON_VALUE [MSG_JSON_VALUE ...]
                        Get the value of the given key from the data of the
                        message content json class structure formatted output,
                        support string array
  -p PACKAGE, --package PACKAGE
                        Filter logs with package
  -pe PACKAGE_EXCLUDE [PACKAGE_EXCLUDE ...], --package_exclude PACKAGE_EXCLUDE [PACKAGE_EXCLUDE ...]
                        Use package name to exclude logs, support string array

ext:
  -i, --tag_case        Filter tags using matching case pattern
  -e, --tag_exact       Filter tags using full match mode
  -a, --all_package     Do not filter packages

```