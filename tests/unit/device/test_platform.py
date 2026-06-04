from __future__ import annotations

from aklog.device.platform import (
    PLATFORM_ANDROID,
    PLATFORM_HARMONY,
    DeviceInfo,
)


class TestDeviceInfo:
    def test_str_representation(self):
        info = DeviceInfo(PLATFORM_ANDROID, "serial123", "Pixel")
        text = str(info)
        assert "android" in text
        assert "serial123" in text
        assert "Pixel" in text

    def test_harmony_platform_constant(self):
        info = DeviceInfo(PLATFORM_HARMONY, "target-1", "target-1")
        assert info.platform == PLATFORM_HARMONY
