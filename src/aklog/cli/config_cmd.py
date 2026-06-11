#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from aklog.core.config import config_path, init_config_file, migrate_config_file


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
    if action == "migrate":
        path, created = migrate_config_file()
        if created:
            print("Migrated config file: {0}".format(path))
        else:
            print("No migration needed: {0}".format(path))
        return True
    if action == "console":
        from aklog.cli.config_interactive import run_config_console

        run_config_console()
        return True
    if action == "filter":
        from aklog.cli.config_filter import run_filter_command

        sub = args.get("filter_action")
        if not sub:
            print("Usage: aklog config filter <list|show|use|get|set|unset|new|delete|edit>")
            return True
        run_filter_command(sub, args)
        return True
    if action == "colors":
        from aklog.cli.config_colors import run_colors_command

        run_colors_command(args.get("colors_action"), args)
        return True
    print("Unknown config action: {0}".format(action))
    return True
