import plistlib
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_OC = ROOT / "dist" / "EFI" / "OC"
OCVALIDATE = ROOT / "deps" / "OpenCore-1.0.8" / "Utilities" / "ocvalidate" / "ocvalidate.exe"


def load_plist(name: str) -> dict:
    return plistlib.loads((DIST_OC / name).read_bytes())


def test_ocvalidate_passes_both_configs():
    for name in ("config.plist", "config-install.plist"):
        plist_path = DIST_OC / name
        assert plist_path.is_file(), f"Missing {plist_path}"
        res = subprocess.run([str(OCVALIDATE), str(plist_path)], capture_output=True, text=True)
        assert "No issues found" in res.stdout, f"{name} failed ocvalidate:\n{res.stdout}\n{res.stderr}"


def test_xps_specific_items_removed_and_inspiron_added():
    cfg = load_plist("config.plist")
    acpi_names = [a["Path"] for a in cfg["ACPI"]["Add"] if a["Enabled"]]
    assert "SSDT-XPS-I2C.aml" not in acpi_names
    assert "SSDT-PLUG-ALT.aml" not in acpi_names
    assert "SSDT-I2C1.aml" in acpi_names
    assert "SSDT-PLUG.aml" in acpi_names

    assert (DIST_OC / "Drivers" / "HfsPlus.efi").is_file()
    driver_paths = [d["Path"] for d in cfg["UEFI"]["Drivers"] if d["Enabled"]]
    assert "HfsPlus.efi" in driver_paths

    kext_paths = {k["BundlePath"]: k["Enabled"] for k in cfg["Kernel"]["Add"]}
    assert kext_paths.get("CpuTopologyRebuild.kext", False) is False
    assert kext_paths.get("XHCI-unsupported.kext", False) is False
    assert kext_paths.get("UTBDefault.kext", False) is False
    assert kext_paths.get("UTBMap.kext") is True
    assert kext_paths.get("AppleALC.kext") is True
    assert kext_paths.get("NootedGreen.kext") is True

    cfg_inst = load_plist("config-install.plist")
    inst_kexts = {k["BundlePath"]: k["Enabled"] for k in cfg_inst["Kernel"]["Add"]}
    assert inst_kexts.get("NootedGreen.kext") is False


def test_nvram_boot_args_and_smbios_populated():
    nvram_guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
    for name in ("config.plist", "config-install.plist"):
        cfg = load_plist(name)
        assert "boot-args" in cfg["NVRAM"]["Delete"][nvram_guid]
        generic = cfg["PlatformInfo"]["Generic"]
        assert generic["SystemProductName"] == "MacBookPro16,2"
        assert len(generic["SystemSerialNumber"]) >= 10
        assert "CHANGE_ME" not in generic["SystemSerialNumber"]

    accel_args = load_plist("config.plist")["NVRAM"]["Add"][nvram_guid]["boot-args"]
    assert "-ngreentglwithgfx" in accel_args
    assert "ngreen-dmc=adlp" not in accel_args

    inst_args = load_plist("config-install.plist")["NVRAM"]["Add"][nvram_guid]["boot-args"]
    assert "-igfxvesa" in inst_args


class TestEfiConfig(unittest.TestCase):
    def test_ocvalidate(self):
        test_ocvalidate_passes_both_configs()

    def test_items(self):
        test_xps_specific_items_removed_and_inspiron_added()

    def test_nvram_and_smbios(self):
        test_nvram_boot_args_and_smbios_populated()


if __name__ == "__main__":
    unittest.main()
