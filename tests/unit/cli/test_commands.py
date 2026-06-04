from __future__ import annotations

from unittest.mock import MagicMock, patch

from aklog.cli import commands


class TestRunLog:
    def test_streams_lines_to_parser(self):
        platform = MagicMock()
        log_printer = MagicMock()
        proc = MagicMock()
        proc.poll.side_effect = [None, None, 0]
        proc.stdout.readline.side_effect = [
            "[ 01-01 00:00:00.000  1: 1 I/Tag ]\n",
            "hello\n",
            "",
        ]
        platform.start_log_stream.return_value = proc
        parser = MagicMock()
        parser.log = None
        platform.create_log_parser.return_value = parser

        with patch("aklog.cli.commands.AppInfoHelper.start"):
            commands.run_log(platform, log_printer)

        platform.check_connect.assert_called_once()
        assert parser.parser.call_count >= 1

    def test_main_runs_log_when_no_subcommand(self):
        fake_platform = MagicMock()
        with (
            patch("aklog.cli.commands.resolve_device", return_value=fake_platform),
            patch("aklog.cli.commands.run_log") as run_log_mock,
        ):
            commands.main([])
        run_log_mock.assert_called_once()

    def test_main_returns_early_on_subcommand(self):
        fake_platform = MagicMock()
        with (
            patch("aklog.cli.commands.resolve_device", return_value=fake_platform),
            patch("aklog.cli.args.AkLogCli.run_command", return_value=True),
            patch("aklog.cli.commands.run_log") as run_log_mock,
        ):
            commands.main(["cap-screen"])
        run_log_mock.assert_not_called()
