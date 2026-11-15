import plistlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INFO = ROOT / "acpi_custom" / "UTBMap.kext" / "Contents" / "Info.plist"


def test_utbmap_valid_and_within_15_port_limit():
    assert INFO.is_file()
    data = plistlib.loads(INFO.read_bytes())
    personalities = data["IOKitPersonalities"]
    assert len(personalities) >= 1
    for name, p in personalities.items():
        assert p["model"] == "MacBookPro16,2"
        ports = p["IOProviderMergeProperties"]["ports"]
        assert len(ports) <= 15, f"{name} exceeds 15-port limit: {len(ports)}"


class TestUsbMap(unittest.TestCase):
    def test_usbmap(self):
        test_utbmap_valid_and_within_15_port_limit()


if __name__ == "__main__":
    unittest.main()
