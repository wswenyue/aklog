import os
import subprocess

import comm_tools


class HdcCmd(object):
    _hdc = None
    _target = None
    _open_log = False

    def __init__(self, open_log=False):
        self._open_log = open_log

    @staticmethod
    def find_hdc(adb_path: str = None) -> str:
        if comm_tools.is_not_empty(HdcCmd._hdc):
            return HdcCmd._hdc
        _path = None
        if comm_tools.is_empty(adb_path):
            if "HARMONY_HOME" in os.environ:
                if comm_tools.is_windows_os():
                    path = comm_tools.find_file("/sdk/*/openharmony/toolchains/hdc.exe", os.environ["HARMONY_HOME"])
                    if os.path.exists(path):
                        _path = path
                    else:
                        raise EnvironmentError(
                            "hdc not found in $HARMONY_HOME path: %s." % os.environ["HARMONY_HOME"])
                else:
                    path = comm_tools.find_file("/sdk/*/openharmony/toolchains/hdc", os.environ["HARMONY_HOME"])
                    if os.path.exists(path):
                        _path = path
                    else:
                        raise EnvironmentError(
                            "hdc not found in $HARMONY_HOME path: %s." % os.environ["HARMONY_HOME"])
            else:
                if comm_tools.is_windows_os():
                    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib", "hdc.exe")
                    if os.path.exists(path):
                        _path = path
                    else:
                        raise EnvironmentError(
                            "hdc not found in $HARMONY_HOME path: %s." % os.environ["HARMONY_HOME"])
                else:
                    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib", "hdc")
                    if os.path.exists(path):
                        _path = path
                    else:
                        raise EnvironmentError(
                            "hdc not found in $HARMONY_HOME path: %s." % os.environ["HARMONY_HOME"])

        else:
            _path = adb_path

        if not comm_tools.is_exe(_path):
            raise ValueError(f"the {_path} is not executable file!!!")
        else:
            HdcCmd._hdc = _path
        return HdcCmd._hdc

    def hdc(self):
        if self._hdc is None:
            self._hdc = self.find_hdc()
        return self._hdc

    def __check_connect(self):
        _cmd = f"{self.hdc()} list targets"
        for line in comm_tools.cmd_run_iter(_cmd):
            if comm_tools.is_empty(line):
                continue
            line = line.strip()
            if line == "[Empty]":
                return False
            else:
                self._target = line
                return True
        return False

    def __restart_connect(self):
        os.system(f"{self.hdc()} kill -r && {self.hdc()} list targets -v")

    def check_connect(self):
        if self.__check_connect():
            return True
        self.__restart_connect()
        if self.__check_connect():
            return True
        raise ValueError("hdc not connection!!! Please check!!!")

    def run_cmd_result_code(self, cmd):
        self.check_connect()
        _cmd = f"{self.hdc()} -t {self._target} {cmd}"
        if self._open_log:
            print(f"run {_cmd}")
        process = subprocess.Popen(str(_cmd).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return process.returncode, out, err

    def run_cmd(self, cmd) -> str:
        code, out, err = self.run_cmd_result_code(cmd)
        if code:
            if self._open_log:
                print(f"error: {err}")
            raise subprocess.CalledProcessError(code, cmd)
        return comm_tools.get_str(out)

    def cmd_run_iter(self, cmd):
        self.check_connect()
        popen = self.popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield comm_tools.get_str(stdout_line)
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def popen(self, cmd, buf_size=None,
              stdout=None, stderr=None,
              universal_newlines=None) -> subprocess.Popen:
        _cmd = f"{self.hdc()} -t {self._target} {cmd}"
        if self._open_log:
            print(f"run {_cmd}")
        return subprocess.Popen(str(_cmd).split(), bufsize=buf_size, stdout=stdout, stderr=stderr,
                                universal_newlines=universal_newlines)
