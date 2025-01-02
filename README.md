# aklog  - Android developer's Swiss Army Knife for Logcat

*See original repo for packaging, installation and other info!*

### How to use

```shell
usage: aklog.py [-h] [-v] [-pc | -pa | -p PACKAGE [PACKAGE ...] |
                -pn PACKAGE_NOT [PACKAGE_NOT ...]]
                [-tnf TAG_NOT_FUZZY [TAG_NOT_FUZZY ...] |
                -tn TAG_NOT [TAG_NOT ...]] [-t TAG [TAG ...] |
                -te TAG_EXACT [TAG_EXACT ...]] [-mn MSG_NOT [MSG_NOT ...]]
                [-m MSG [MSG ...] |
                -mjson MSG_JSON_VALUE [MSG_JSON_VALUE ...]] [-l LEVEL]
                [-cs [CMD_SCREEN_CAP] | -cr [CMD_RECORD_VIDEO]]

AKLog - Android Developer's Swiss Army Knife for Log (Version v5.0.5)

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -pc, --package_current_top
                        Match logs from the currently top foreground
                        application. This is the default condition if no
                        package filter is specified.
  -pa, --package_all    Show logs from all packages without filtering.
  -p, --package PACKAGE [PACKAGE ...]
                        Match logs from specified package(s). You do not need
                        to provide the full package name; partial names are
                        sufficient.
  -pn, --package_not PACKAGE_NOT [PACKAGE_NOT ...]
                        Exclude logs from specified package(s), supports
                        multiple values.
  -tnf, --tag_not_fuzzy TAG_NOT_FUZZY [TAG_NOT_FUZZY ...]
                        Fuzzy match tags and filter out logs that do not
                        match. Supports multiple values, e.g., -tnf tag1 tag2.
  -tn, --tag_not TAG_NOT [TAG_NOT ...]
                        Match tags and filter out logs that do not match.
                        Supports multiple values, e.g., -tn tag1 tag2.
  -t, --tag TAG [TAG ...]
                        Match specific tags. Supports multiple values, e.g.,
                        -t tag1 tag2.
  -te, --tag_exact TAG_EXACT [TAG_EXACT ...]
                        Match exact tags. Supports multiple values, e.g., -te
                        tag1 tag2.
  -mn, --msg_not MSG_NOT [MSG_NOT ...]
                        Match log content keywords and filter out logs that do
                        not match. Supports multiple values, e.g., -mn msg1
                        msg2.
  -m, --msg MSG [MSG ...]
                        Match log content keywords. Supports multiple values,
                        e.g., -m msg1 msg2.
  -mjson, --msg_json_value MSG_JSON_VALUE [MSG_JSON_VALUE ...]
                        Match JSON data in log content and extract specified
                        key values. For example, -mjson keyA keyB will match
                        logs with "keyA" or "keyB" in JSON data and extract
                        the corresponding values.
  -l, --level LEVEL     Match log levels (V|v|2, D|d|3, I|i|4, W|w|5, E|e|6).
  -cs, --cmd_screen_cap [CMD_SCREEN_CAP]
                        Command: Capture the current phone screen and save it
                        to the specified location (or the default location if
                        none is provided): ~/Desktop/AkScreen/
  -cr, --cmd_record_video [CMD_RECORD_VIDEO]
                        Command: Start recording the current phone screen and
                        save it to the specified location (or the default
                        location if none is provided): ~/Desktop/AkRVideo/

```
