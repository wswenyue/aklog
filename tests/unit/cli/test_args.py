from __future__ import annotations

import pytest

from aklog.cli.args import AkLogCli
from aklog.log.filters import PackageFilterType


@pytest.fixture
def cli():
    return AkLogCli()


class TestAkLogCliParse:
    def test_version_string_from_build_meta(self, cli):
        assert cli.AK_LOG_VERSION.startswith("v")

    def test_default_package_is_current_top(self, cli):
        args = cli.parse([])
        assert args["package_current_top"] is True
        assert args["package_all"] is False

    def test_package_all_flag(self, cli):
        args = cli.parse(["-pa"])
        printer = cli.build_log_printer(args)
        assert printer.package.type == PackageFilterType.All

    def test_package_target(self, cli):
        args = cli.parse(["-p", "com.example.app"])
        printer = cli.build_log_printer(args)
        assert printer.package.type == PackageFilterType.TARGET
        assert "com.example.app" in printer.package.target_package

    def test_package_exclude(self, cli):
        args = cli.parse(["-pn", "system"])
        printer = cli.build_log_printer(args)
        assert printer.package.type == PackageFilterType.EXCLUDE

    def test_tag_exact(self, cli):
        args = cli.parse(["-te", "MyTag"])
        printer = cli.build_log_printer(args)
        assert printer.tag.is_exact is True
        assert printer.tag.target == ["MyTag"]

    def test_tag_not_fuzzy(self, cli):
        args = cli.parse(["-tnf", "Noise"])
        printer = cli.build_log_printer(args)
        assert printer.tag.is_tag_not_fuzzy is True
        assert printer.tag.tag_not == ["Noise"]

    def test_msg_keyword(self, cli):
        args = cli.parse(["-m", "error"])
        printer = cli.build_log_printer(args)
        assert printer.msg.target == ["error"]

    def test_msg_json(self, cli):
        args = cli.parse(["-mjson", "userId"])
        out = cli.build_log_printer(args).msg.format_content('{"userId":"1"}')
        assert out is not None

    def test_level_filter(self, cli):
        args = cli.parse(["-l", "E"])
        assert cli.build_log_printer(args).level.filter("E") is True

    def test_invalid_level_raises(self, cli):
        args = cli.parse(["-l", "?"])
        with pytest.raises(ValueError, match="level filter"):
            cli.build_log_printer(args)

    def test_device_option(self, cli):
        args = cli.parse(["-d", "emulator-5554"])
        assert args["device"] == "emulator-5554"

    def test_empty_msg_filter_raises(self, cli):
        args = cli.parse([])
        args[cli.dest_msg] = [""]
        with pytest.raises(ValueError, match="msg filter"):
            cli._parser_args_msg(args)


class TestAkLogCliCommands:
    def test_run_cap_screen(self, cli, monkeypatch):
        captured = {}

        class FakeCap:
            def __init__(self, platform, _dir):
                captured["dir"] = _dir

            def do_capture(self):
                captured["done"] = True

        monkeypatch.setattr("aklog.cli.args.ScreenCapTools", FakeCap)
        args = cli.parse(["cap-screen", "-path", "/tmp/cap"])
        assert cli.run_command(object(), args) is True
        assert captured["dir"] == "/tmp/cap"
        assert captured["done"] is True

    def test_run_install(self, cli, monkeypatch):
        installed = {}

        class FakePlatform:
            def install_package(self, path):
                installed["path"] = path

        args = cli.parse(["install", "-path", "/tmp/app.apk"])
        assert cli.run_command(FakePlatform(), args) is True
        assert installed["path"] == "/tmp/app.apk"

    def test_no_subcommand_returns_false(self, cli):
        class FakePlatform:
            pass

        args = cli.parse([])
        assert cli.run_command(FakePlatform(), args) is False
