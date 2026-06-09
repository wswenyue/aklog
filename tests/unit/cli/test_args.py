from __future__ import annotations

import pytest

from aklog.cli.args import AkLogCli
from aklog.log.filter import PackageMode


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
        package_filter = cli._build_package_filter(args)
        assert package_filter.mode == PackageMode.ALL

    def test_package_target(self, cli):
        args = cli.parse(["-p", "com.example.app"])
        package_filter = cli._build_package_filter(args)
        assert package_filter.mode == PackageMode.TARGET
        assert "com.example.app" in package_filter.targets

    def test_package_exclude(self, cli):
        args = cli.parse(["-pn", "system"])
        package_filter = cli._build_package_filter(args)
        assert package_filter.mode == PackageMode.EXCLUDE

    def test_tag_exact(self, cli):
        args = cli.parse(["-te", "MyTag"])
        tag_filter = cli._build_tag_filter(args)
        assert tag_filter.exact is True
        assert tag_filter.include == ["MyTag"]

    def test_tag_not(self, cli):
        args = cli.parse(["-tn", "wlog"])
        tag_filter = cli._build_tag_filter(args)
        assert tag_filter.exclude_fuzzy == ["wlog"]
        assert tag_filter.accept_tag("com.wuba.bangjob.hap/wlog-c") is False
        assert tag_filter.accept_tag("other-tag") is True

    def test_tag_not_exact(self, cli):
        args = cli.parse(["-ten", "MyTag"])
        tag_filter = cli._build_tag_filter(args)
        assert tag_filter.exclude_exact == ["MyTag"]
        assert tag_filter.accept_tag("MyTag") is False
        assert tag_filter.accept_tag("MyTagExtra") is True

    def test_tag_not_fuzzy_and_exact_together(self, cli):
        args = cli.parse(["-tn", "Noise", "-ten", "ExactTag"])
        tag_filter = cli._build_tag_filter(args)
        assert tag_filter.exclude_fuzzy == ["Noise"]
        assert tag_filter.exclude_exact == ["ExactTag"]
        assert tag_filter.accept_tag("NoiseTag") is False
        assert tag_filter.accept_tag("ExactTag") is False
        assert tag_filter.accept_tag("CleanTag") is True

    def test_msg_keyword(self, cli):
        args = cli.parse(["-m", "error"])
        msg_processor = cli._build_msg_processor(args)
        assert msg_processor.include == ["error"]
        assert msg_processor.exact is False
        assert msg_processor.process("got ERROR here") == "got ERROR here"

    def test_msg_exact(self, cli):
        args = cli.parse(["-me", "error"])
        msg_processor = cli._build_msg_processor(args)
        assert msg_processor.include == ["error"]
        assert msg_processor.exact is True
        assert msg_processor.process("error") == "error"
        assert msg_processor.process("got error here") is None

    def test_msg_not_fuzzy(self, cli):
        args = cli.parse(["-mn", "secret"])
        msg_processor = cli._build_msg_processor(args)
        assert msg_processor.exclude_fuzzy == ["secret"]
        assert msg_processor.process("contains SECRET") is None

    def test_msg_not_exact(self, cli):
        args = cli.parse(["-men", "error"])
        msg_processor = cli._build_msg_processor(args)
        assert msg_processor.exclude_exact == ["error"]
        assert msg_processor.process("error") is None
        assert msg_processor.process("got error here") == "got error here"

    def test_msg_not_fuzzy_and_exact_together(self, cli):
        args = cli.parse(["-mn", "noise", "-men", "ExactMsg"])
        msg_processor = cli._build_msg_processor(args)
        assert msg_processor.process("Noise here") is None
        assert msg_processor.process("ExactMsg") is None
        assert msg_processor.process("clean") == "clean"

    def test_msg_json(self, cli):
        args = cli.parse(["-mjson", "userId"])
        out = cli._build_msg_processor(args).process('{"userId":"1"}')
        assert out is not None

    def test_level_filter(self, cli):
        args = cli.parse(["-l", "E"])
        assert cli._build_level_filter(args).accept_level("E") is True

    def test_invalid_level_raises(self, cli):
        args = cli.parse(["-l", "?"])
        with pytest.raises(ValueError, match="level filter"):
            cli._build_level_filter(args)

    def test_device_option(self, cli):
        args = cli.parse(["-d", "emulator-5554"])
        assert args["device"] == "emulator-5554"

    def test_empty_msg_filter_raises(self, cli):
        args = cli.parse([])
        args[cli.dest_msg] = [""]
        with pytest.raises(ValueError, match="msg filter"):
            cli._build_msg_processor(args)

    def test_empty_msg_exact_filter_raises(self, cli):
        args = cli.parse([])
        args[cli.dest_msg_exact] = [""]
        with pytest.raises(ValueError, match="msg filter"):
            cli._build_msg_processor(args)


class TestAkLogCliBuildLogPrinter:
    def test_default_builds_top_package_filter(self, cli):
        printer = cli.build_log_printer(cli.parse([]))
        package_filter = printer.filters.filters[0]
        assert package_filter.mode == PackageMode.TOP

    def test_build_log_printer_wires_full_filter_chain(self, cli):
        args = cli.parse(["-pa", "-te", "MyTag", "-m", "error", "-l", "W"])
        printer = cli.build_log_printer(args)
        package_filter, level_filter, tag_filter = printer.filters.filters
        assert package_filter.mode == PackageMode.ALL
        assert tag_filter.exact is True
        assert tag_filter.include == ["MyTag"]
        assert printer.msg_processor.include == ["error"]
        assert level_filter.accept_level("W") is True
        assert level_filter.accept_level("I") is False

    def test_msg_not_with_json(self, cli):
        args = cli.parse(["-mn", "secret", "-mjson", "userId"])
        processor = cli._build_msg_processor(args)
        assert processor.process('{"userId":"1"}') is not None
        assert processor.process('secret {"userId":"1"}') is None


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

    def test_run_config_path(self, cli, capsys):
        args = cli.parse(["config", "path"])
        assert cli.run_command(object(), args) is True
        captured = capsys.readouterr()
        assert "config.toml" in captured.out

    def test_run_config_init(self, cli, monkeypatch, tmp_path, capsys):
        config_path = tmp_path / "config.toml"
        monkeypatch.setattr("aklog.cli.config_cmd.config_path", lambda: str(config_path))
        monkeypatch.setattr("aklog.cli.config_cmd.init_config_file", lambda force=False: (str(config_path), True))
        args = cli.parse(["config", "init"])
        assert cli.run_command(object(), args) is True
        captured = capsys.readouterr()
        assert str(config_path) in captured.out
