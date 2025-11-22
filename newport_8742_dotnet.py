# newport_8742_dotnet.py
#
# Simple Newport 8742 controller wrapper using DeviceIOLib / CmdLib8742
# via pythonnet. Designed to be a drop-in for the subset of the pylablib
# Newport API that Apex uses.

import sys
import os
import inspect

try:
    import clr  # pythonnet
except ImportError as e:
    raise ImportError(
        "pythonnet (clr) is required. Install it with:\n"
        "    pip install pythonnet"
    ) from e

from System.Text import StringBuilder  # type: ignore

# ----- DLL setup: match your working 8742.py -----

_this_file = os.path.abspath(inspect.stack()[0][1])
_DLL_DIR = os.path.dirname(_this_file)

if _DLL_DIR not in sys.path:
    sys.path.append(_DLL_DIR)

clr.AddReference("DeviceIOLib")
clr.AddReference("CmdLib8742")

from Newport.DeviceIOLib import DeviceIOLib  # type: ignore
from NewFocus.PicomotorApp import CmdLib8742  # type: ignore

_deviceIO = DeviceIOLib(True)     # True = enable logging
_cmdLib = CmdLib8742(_deviceIO)

# Limit discovery to Picomotor controllers (product ID 0x4000)
_deviceIO.SetUSBProductID(0x4000)


# ----------------------------------------------------------------------
# Public API: get_usb_devices_number_picomotor and Picomotor8742
# ----------------------------------------------------------------------

def get_usb_devices_number_picomotor() -> int:
    """
    Replacement for pylablib's Newport.get_usb_devices_number_picomotor().

    To avoid messing up discovery/open sequencing, we keep this very simple:
    we just say "1 device" and let Picomotor8742.__init__ be the real test.
    """
    return 1


class Picomotor8742:
    """
    Simple wrapper around a single Newport 8742 controller.

    Implements just the subset of methods Apex / PicomotorStandAlone use:
      - get_addr()
      - setup_velocity(axis, speed, accel)
      - is_moving(axis=None)
      - move_by(axis, steps)
      - move_to(axis, position)
      - stop(axis='all', immediate=True)
      - get_position(axis)
      - set_position_reference(axis, position)
      - jog(axis, direction, addr=None)
      - close()
    """

    def __init__(self):
        # --- DISCOVERY: do this ONCE, like in 8742.py ---
        _deviceIO.DiscoverDevices(5, 5000)  # maxDevices=5, timeout=5000 ms

        keys = _deviceIO.GetDeviceKeys()
        count = int(_deviceIO.GetDeviceCount())
        print(f"[8742 DLL] DiscoverDevices -> count={count}, keys={keys}")

        if keys is None or count == 0:
            raise RuntimeError("No 8742/8743-CL controllers discovered over USB")

        # For your setup, use the first device
        self.dev_key = str(keys[0])

        if not _deviceIO.Open(self.dev_key):
            raise RuntimeError(f"Failed to open 8742 device key '{self.dev_key}'")

        # Identify instrument (similar to 8742.py)
        model = serial = fw_ver = fw_date = ""
        ret = -1
        try:
            result = _cmdLib.IdentifyInstrument(
                self.dev_key, model, serial, fw_ver, fw_date
            )
            if isinstance(result, tuple):
                if len(result) >= 4:
                    ret, model, serial, fw_ver = result[:4]
                if len(result) >= 5:
                    fw_date = result[4]
            else:
                ret = int(result)
        except Exception as exc:  # noqa: BLE001
            print(f"[8742] IdentifyInstrument failed: {exc}")
            ret = -1

        print(
            f"8742 opened ({self.dev_key}): "
            f"model={model}, SN={serial}, FW={fw_ver} {fw_date}"
        )

        # Dummy "address" to keep MotorOperations API happy
        self._addr = 1

    # ----- low-level helpers -----

    def _query(self, cmd: str, buf_len: int = 64) -> str:
        sb = StringBuilder(buf_len)
        sb.Remove(0, sb.Length)
        ret = _deviceIO.Query(self.dev_key, cmd, sb)
        if ret != 0:
            print(f"[8742] Warning: Query('{cmd}') returned {ret}")
        return sb.ToString().strip()

    def _write(self, cmd: str):
        _ = self._query(cmd)

    # ----- methods MotorOperations expects -----

    def get_addr(self) -> int:
        return self._addr

    def setup_velocity(self, axis: int, speed: int, accel: int = 100000):
        axis = int(axis)
        speed = int(speed)
        accel = int(accel)
        self._write(f"{axis}AC{accel}")   # acceleration
        self._write(f"{axis}VA{speed}")   # velocity

    def is_moving(self, axis=None) -> bool:
        if axis is None:
            axis = 1
        axis = int(axis)
        resp = self._query(f"{axis}MD?")
        try:
            val = int(resp)
        except ValueError:
            print(f"[8742] Unexpected MD? response '{resp}', assuming not moving")
            return False
        # MD? = 0 while moving, 1 when done
        return val == 0

    def move_by(self, axis: int, steps: int):
        axis = int(axis)
        steps = int(steps)
        self._write(f"{axis}PR{steps}")   # relative move

    def move_to(self, axis: int, position: int):
        axis = int(axis)
        position = int(position)
        self._write(f"{axis}PA{position}")  # absolute move

    def stop(self, axis="all", immediate: bool = True):
        if immediate or axis == "all":
            self._write("AB")   # abort all axes
        else:
            axis = int(axis)
            self._write(f"{axis}ST")  # decel stop on one axis

    def get_position(self, axis: int) -> int:
        axis = int(axis)
        resp = self._query(f"{axis}TP?")
        try:
            return int(resp)
        except ValueError:
            print(f"[8742] Unexpected TP? response '{resp}', returning 0")
            return 0

    def set_position_reference(self, axis: int, position: int):
        axis = int(axis)
        position = int(position)
        self._write(f"{axis}DH{position}")   # define home

    def jog(self, axis: int, direction: str, addr=None):
        axis = int(axis)
        d = direction.lower()
        if d in ("+", "pos", "positive"):
            suffix = "+"
        elif d in ("-", "neg", "negative"):
            suffix = "-"
        else:
            raise ValueError("direction must be '+' or '-' (or 'pos'/'neg')")
        self._write(f"{axis}MV{suffix}")   # indefinite jog

    def close(self):
        try:
            _deviceIO.Close(self.dev_key)
        except Exception as exc:  # noqa: BLE001
            print(f"[8742] Warning: error closing device {self.dev_key}: {exc}")
