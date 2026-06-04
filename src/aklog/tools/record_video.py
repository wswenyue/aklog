#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import signal
import time

from aklog.core import comm_tools


class PhoneRecordVideo:
    DEF_PATH_FILE_NAME = "AkRVideo"
    def_record_video_path = "~/Desktop/{0}/".format(DEF_PATH_FILE_NAME)
    isDoExitWork = False

    def __init__(self, platform, _dir=None):
        self._platform = platform
        self.videoName = "R" + time.strftime("%m%d%H%M%S", time.localtime()) + ".mp4"
        if comm_tools.is_empty(_dir):
            self.phone_save_path = os.path.join(
                comm_tools.get_user_desktop_dir("{0}/".format(self.DEF_PATH_FILE_NAME)), self.videoName
            )
        else:
            self.phone_save_path = os.path.join(_dir, self.videoName)
        comm_tools.create_dir_not_exists(self.phone_save_path)
        self._record_proc = None
        self._phone_video = None

    def do_record(self):
        if self._platform.platform == "android":
            self._record_proc = self._platform.start_screen_record(self.videoName)
            if self._record_proc:
                self._record_proc.wait()
            print("do_record succeed")
        else:
            self._platform.start_screen_record(self.videoName)
            print("do_record started (HarmonyOS). Press Ctrl+C to stop.")
            while not self.isDoExitWork:
                time.sleep(1)

    def do_pull(self):
        if self._platform.platform == "android":
            phone_path = self._platform.stop_screen_record(self.videoName)
            self._platform.pull_file(phone_path, self.phone_save_path)
        else:
            phone_path = self._platform.stop_screen_record(self.videoName)
            if phone_path != self.videoName:
                self._platform.pull_file(phone_path, self.phone_save_path)
            else:
                print("warning: could not resolve record file path, try mediatool manually")
        print("do_pull succeed")

    def do_clean(self):
        if self._platform.platform == "android":
            phone_path = getattr(self._platform, "_record_phone_path", None)
            if phone_path:
                self._platform.remove_remote_file(phone_path)
        print("do_clean succeed")


class RecordHelper:
    curRecord = None

    @staticmethod
    def _exit(signum, frame):
        if RecordHelper.curRecord is None:
            exit()
            return
        if RecordHelper.curRecord.isDoExitWork:
            exit()
        RecordHelper.curRecord.isDoExitWork = True
        print("\nwait phone save video finish...")
        time.sleep(2)
        print("do pull video file...")
        RecordHelper.curRecord.do_pull()
        RecordHelper.curRecord.do_clean()
        print("finish.")
        RecordHelper.curRecord = None
        exit()

    @staticmethod
    def do_work(platform, _dir=None):
        RecordHelper.curRecord = PhoneRecordVideo(platform, _dir)
        signal.signal(signal.SIGINT, RecordHelper._exit)
        signal.signal(signal.SIGTERM, RecordHelper._exit)
        RecordHelper.curRecord.do_record()
