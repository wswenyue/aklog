#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/8/30 
"""
import os.path
import signal
import time

import comm_tools
from adb_utils import AdbHelper


class PhoneRecordVideo(object):
    DEF_PATH_FILE_NAME = "AkRVideo"
    isDoExitWork = False

    def __init__(self, _dir: str = None):
        self.videoName = "R" + time.strftime("%m%d%H%M%S", time.localtime()) + ".mp4"
        self.phone_video = "/sdcard/" + self.videoName
        if comm_tools.is_empty(_dir):
            self.phone_save_path = os.path.join(comm_tools.get_user_desktop_dir(f"{self.DEF_PATH_FILE_NAME}/"),
                                                self.videoName)
        else:
            self.phone_save_path = os.path.join(_dir, self.videoName)
        comm_tools.create_dir_not_exists(self.phone_save_path)

    def do_record(self):
        code, out, err = AdbHelper().run_cmd_result_code(f"shell screenrecord {self.phone_video}")
        if code == 0:
            print("do_record succeed")
        else:
            print(f"do_record error:{out}")

    def do_pull(self):
        code, out, err = AdbHelper().run_cmd_result_code(f"pull {self.phone_video} {self.phone_save_path}")
        if code == 0:
            print("do_pull succeed")
        else:
            print(f"do_pull error:{out}")

    def do_clean(self):
        code, out, err = AdbHelper().run_cmd_result_code(f"shell rm {self.phone_video}")
        if code == 0:
            print("do_clean succeed")
        else:
            print(f"do_clean error:{out}")


class RecordHelper(object):
    curRecord: PhoneRecordVideo = None

    @staticmethod
    def _exit(signum, frame):
        if RecordHelper.curRecord is None:
            exit()
            return
        if RecordHelper.curRecord.isDoExitWork:
            exit()
        RecordHelper.curRecord.isDoExitWork = True
        print('\nwait phone save video finish...')
        time.sleep(2)
        print("do pull video file...")
        RecordHelper.curRecord.do_pull()
        # time.sleep(10)
        RecordHelper.curRecord.do_clean()
        print('finish.')
        RecordHelper.curRecord = None
        exit()

    @staticmethod
    def do_work(_dir: str = None):
        RecordHelper.curRecord = PhoneRecordVideo(_dir)
        signal.signal(signal.SIGINT, RecordHelper._exit)
        signal.signal(signal.SIGTERM, RecordHelper._exit)
        RecordHelper.curRecord.do_record()

#
# if __name__ == '__main__':
#     do_work()
