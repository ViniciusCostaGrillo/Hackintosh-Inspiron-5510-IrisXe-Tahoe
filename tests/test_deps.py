import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / "deps"


def test_required_binaries_and_repos_exist():
    assert (DEPS / "Hackintosh-XPS13Plus-IrisXe-Tahoe" / "EFI" / "OC" / "config.plist").is_file()
    assert (DEPS / "OpenCore-1.0.8" / "Utilities" / "ocvalidate" / "ocvalidate.exe").is_file()
    assert (DEPS / "OpenCore-1.0.8" / "Utilities" / "macserial" / "macserial.exe").is_file()
    assert (DEPS / "OcBinaryData" / "Drivers" / "HfsPlus.efi").is_file()
    assert (DEPS / "AppleALC" / "AppleALC.kext" / "Contents" / "Info.plist").is_file()
    assert (DEPS / "acpica" / "iasl.exe").is_file()


class TestDeps(unittest.TestCase):
    def test_deps(self):
        test_required_binaries_and_repos_exist()


if __name__ == "__main__":
    unittest.main()
