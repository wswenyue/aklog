#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from aklog.core.config import config_path, init_config_file


def run_config_command(args: dict) -> bool:
    action = args.get("config_action")
    if action == "init":
        path, created = init_config_file(force=bool(args.get("force")))
        if created:
            print("Created config file: {0}".format(path))
        else:
            print("Config file already exists: {0}".format(path))
            print("Use --force to overwrite.")
        return True
    if action == "path":
        print(config_path())
        return True
    print("Unknown config action: {0}".format(action))
    return True
