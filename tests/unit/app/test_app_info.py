from __future__ import annotations

from aklog.app.info import AppInfoHelper


class FakePlatform:
    def __init__(self, fg="com.demo.app", processes=None):
        self._fg = fg
        self._processes = processes or [("100", "com.demo.app"), ("101", "com.demo.app:ui")]

    def get_foreground_package(self):
        return self._fg

    def iter_processes(self):
        return iter(self._processes)


class TestAppInfoHelper:
    def setup_method(self):
        AppInfoHelper._instance = None

    def teardown_method(self):
        AppInfoHelper._instance = None

    def test_cur_app_package_empty_without_instance(self):
        assert AppInfoHelper.cur_app_package() == ""

    def test_found_name_by_pid(self):
        helper = AppInfoHelper(FakePlatform())
        helper._main_process = {"100": "com.demo.app"}
        helper._children_process = {"101": "com.demo.app:ui"}
        AppInfoHelper._instance = helper
        assert AppInfoHelper.found_name_by_pid("100") == "com.demo.app"
        assert AppInfoHelper.found_name_by_pid("101") == "com.demo.app:ui"
        assert AppInfoHelper.found_name_by_pid("999") is None

    def test_is_main_process(self):
        helper = AppInfoHelper(FakePlatform())
        helper._main_process = {"100": "com.demo.app"}
        helper._children_process = {"101": "com.demo.app:ui"}
        AppInfoHelper._instance = helper
        assert AppInfoHelper.is_main_process("100") is True
        assert AppInfoHelper.is_main_process("101") is False
        assert AppInfoHelper.is_main_process("999") is None

    def test_refresh_processes_splits_main_and_child(self):
        helper = AppInfoHelper(FakePlatform())
        helper._refresh_processes()
        assert "100" in helper._main_process
        assert "101" in helper._children_process

    def test_refresh_foreground_package(self):
        helper = AppInfoHelper(FakePlatform(fg="com.new.app"))
        helper._refresh_foreground_package()
        assert helper._cur_app_package == "com.new.app"
        AppInfoHelper._instance = helper
        assert AppInfoHelper.cur_app_package() == "com.new.app"

    def test_start_spawns_background_thread(self, monkeypatch):
        started = {}

        def fake_thread(target, name=None, args=()):
            started["name"] = name
            # Run one refresh cycle only; real _run loops forever.
            helper = AppInfoHelper._instance
            helper._refresh_processes()
            helper._refresh_foreground_package()

        monkeypatch.setattr("aklog.app.info.comm_tools.new_thread", fake_thread)
        AppInfoHelper.start(FakePlatform(), delay=0)
        assert started["name"] == "Thread-FetchAPKInfo"
        assert AppInfoHelper.get_instance() is not None
        assert AppInfoHelper.cur_app_package() == "com.demo.app"
