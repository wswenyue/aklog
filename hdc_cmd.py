import os

import comm_tools


class HdcCmd(object):
    _hdc = None

    @staticmethod
    def find_hdc(adb_path: str = None) -> str:
        if comm_tools.is_not_empty(HdcCmd._hdc):
            return HdcCmd._hdc
        _path = None
        if comm_tools.is_empty(adb_path):
            if "HARMONY_HOME" in os.environ:
                if comm_tools.is_windows_os():
                    path = os.path.join(os.environ["HARMONY_HOME"], "sdk", "HarmonyOS-NEXT-DB1", "openharmony",
                                        "toolchains", "hdc.exe")
                    if os.path.exists(path):
                        _path = path
                    else:
                        raise EnvironmentError(
                            "hdc not found in $HARMONY_HOME path: %s." % os.environ["HARMONY_HOME"])
                else:
                    path = os.path.join(os.environ["HARMONY_HOME"], "sdk", "HarmonyOS-NEXT-DB1", "openharmony",
                                        "toolchains", "hdc")
                    if os.path.exists(path):
                        _path = path
                    else:
                        raise EnvironmentError(
                            "hdc not found in $HARMONY_HOME path: %s." % os.environ["HARMONY_HOME"])
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
