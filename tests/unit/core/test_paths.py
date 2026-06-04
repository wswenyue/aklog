from __future__ import annotations

import platform
from pathlib import Path

from aklog.core import comm_tools
from aklog.core.paths import bundled_lib_dir, bundled_tool, host_arch, host_os, lib_dir, package_dir, project_root


class TestPaths:
    def test_project_layout(self):
        root = project_root()
        pkg = package_dir()
        assert Path(root) == Path(__file__).resolve().parents[3]
        assert Path(pkg) == Path(root) / "src" / "aklog"
        assert Path(lib_dir()) == Path(root) / "lib"

    def test_bundled_lib_dir_under_os_arch(self):
        root = project_root()
        expected = Path(root) / "lib" / host_os() / host_arch()
        assert Path(bundled_lib_dir()) == expected

    def test_bundled_tool_returns_path(self):
        name = "adb.exe" if comm_tools.is_windows_os() else "adb"
        path = bundled_tool(name)
        assert path.endswith(name)
        assert host_os() in path or name in path

    def test_host_arch_normalized(self):
        machine = platform.machine().lower()
        arch = host_arch()
        if machine in ("arm64", "aarch64"):
            assert arch in ("arm64", "aarch64")
        elif machine in ("x86_64", "amd64"):
            assert arch == "x86_64"
