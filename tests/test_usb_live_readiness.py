import hashlib
import plistlib
import struct
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OCVALIDATE = ROOT / "deps" / "OpenCore-1.0.8" / "Utilities" / "ocvalidate" / "ocvalidate.exe"
DSDT_DAT = ROOT / "acpi_dump" / "dsdt.dat"
USB_ROOT = Path("D:/")
USB_OC = USB_ROOT / "EFI" / "OC"


def test_usb_mounted_and_core_files_present():
    assert USB_ROOT.exists(), "USB drive D: is not mounted"
    assert (USB_ROOT / "EFI" / "BOOT" / "BOOTx64.efi").is_file()
    assert (USB_OC / "OpenCore.efi").is_file()
    assert (USB_OC / "config.plist").is_file()
    assert (USB_OC / "config-install.plist").is_file()
    assert (USB_OC / "config-accelerated.plist").is_file()
    assert (USB_ROOT / "irisxe-tahoe-bundle.tar.gz").is_file()
    assert (USB_ROOT / "com.apple.recovery.boot" / "BaseSystem.dmg").is_file()
    assert (USB_ROOT / "com.apple.recovery.boot" / "BaseSystem.chunklist").is_file()


def test_usb_ocvalidate_all_configs():
    for name in ("config.plist", "config-install.plist", "config-accelerated.plist"):
        target = USB_OC / name
        res = subprocess.run([str(OCVALIDATE), str(target)], capture_output=True, text=True)
        assert "No issues found" in res.stdout, f"{name} failed ocvalidate:\n{res.stdout}\n{res.stderr}"


def test_usb_configs_quirks_security_and_boot_args():
    inst = plistlib.loads((USB_OC / "config.plist").read_bytes())
    acc = plistlib.loads((USB_OC / "config-accelerated.plist").read_bytes())

    for cfg_name, cfg in (("install (config.plist)", inst), ("accelerated (config-accelerated.plist)", acc)):
        assert cfg["Misc"]["Boot"]["HideAuxiliary"] is False, f"{cfg_name}: HideAuxiliary must be False"
        assert cfg["Misc"]["Security"]["ScanPolicy"] == 0, f"{cfg_name}: ScanPolicy must be 0"
        assert cfg["Misc"]["Security"]["SecureBootModel"] == "Disabled", f"{cfg_name}: SecureBootModel must be Disabled"
        assert cfg["Misc"]["Security"]["DmgLoading"] == "Signed", f"{cfg_name}: DmgLoading must be Signed"
        assert cfg["UEFI"]["APFS"]["MinDate"] == -1 and cfg["UEFI"]["APFS"]["MinVersion"] == -1
        assert cfg["Kernel"]["Quirks"]["AppleXcpmCfgLock"] is True
        assert cfg["Kernel"]["Quirks"]["CustomSMBIOSGuid"] is True
        assert cfg["PlatformInfo"]["UpdateSMBIOSMode"] == "Custom"

        # Verify Cpuid1Data and Cpuid1Mask include EBX[23:16]=0x80 to prevent divide-by-zero after EXITBS
        assert cfg["Kernel"]["Emulate"]["Cpuid1Data"] == bytes.fromhex("55060A00000080000000000000000000")
        assert cfg["Kernel"]["Emulate"]["Cpuid1Mask"] == bytes.fromhex("FFFFFFFF0000FF000000000000000000")

        # Real SMBIOS serials on USB (not placeholders)
        gen = cfg["PlatformInfo"]["Generic"]
        assert gen["SystemProductName"] == "MacBookPro16,2"
        assert "CHANGE_ME" not in gen["SystemSerialNumber"] and len(gen["SystemSerialNumber"]) >= 10
        assert "CHANGE_ME" not in gen["MLB"] and len(gen["MLB"]) >= 12

        # NVRAM Delete must include boot-args
        boot_guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
        assert "boot-args" in cfg["NVRAM"]["Delete"][boot_guid]

    boot_guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
    inst_args = inst["NVRAM"]["Add"][boot_guid]["boot-args"]
    for flag in ("-v", "-igfxvesa", "-vi2c-force-polling", "amfi_get_out_of_my_way=1", "alcid=11"):
        assert flag in inst_args, f"Missing {flag} in install boot-args: {inst_args}"

    # Safe VESA device-id in install config so TGL kext never attaches unpatched
    inst_gfx = inst["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"]
    assert inst_gfx["device-id"] == bytes.fromhex("FFFF0000")

    acc_args = acc["NVRAM"]["Add"][boot_guid]["boot-args"]
    for flag in (
        "-v",
        "-ngreentglwithgfx",
        "-allow3d",
        "-disablegfxfirmware",
        "ngreen-dmc=tgl",
        "-ngreenv189",
        "-ngreenkeepefi",
        "-ngreenxefix",
        "-ngreenfixbootmode",
        "ngreenSched=4",
        "ngreenV142=3",
        "gfxrst=1",
        "ngreenpm=22",
        "amfi_get_out_of_my_way=1",
        "alcid=11",
    ):
        assert flag in acc_args, f"Missing {flag} in accelerated boot-args: {acc_args}"
    assert "ngreen-dmc=adlp" not in acc_args

    acc_gfx = acc["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"]
    assert acc_gfx["device-id"] == bytes.fromhex("499A0000")
    assert acc_gfx["AAPL,ig-platform-id"] == bytes.fromhex("0000499A")


def test_usb_acpi_tables_and_patches_against_real_dsdt():
    cfg = plistlib.loads((USB_OC / "config-accelerated.plist").read_bytes())
    dsdt_bytes = DSDT_DAT.read_bytes()

    for entry in cfg["ACPI"]["Add"]:
        if not entry.get("Enabled"):
            continue
        aml_file = USB_OC / "ACPI" / entry["Path"]
        assert aml_file.is_file(), f"Missing ACPI table on USB: {aml_file}"
        raw = aml_file.read_bytes()
        assert len(raw) > 36 and raw[:4] == b"SSDT", f"Invalid AML header in {aml_file}"

    for patch in cfg["ACPI"]["Patch"]:
        if not patch.get("Enabled"):
            continue
        find_bytes = patch["Find"]
        repl_bytes = patch["Replace"]
        assert len(find_bytes) == len(repl_bytes), f"Patch length mismatch: {patch.get('Comment')}"
        assert dsdt_bytes.count(find_bytes) >= 1, f"ACPI Patch Find bytes not found in Dell DSDT: {patch.get('Comment')}"


def test_usb_drivers_and_kext_binaries_and_load_order():
    MACHO_MAGICS = {
        b"\xcf\xfa\xed\xfe",  # Mach-O 64-bit little-endian
        b"\xca\xfe\xba\xbe",  # Universal binary big-endian
    }
    for cfg_file in ("config.plist", "config-accelerated.plist"):
        cfg = plistlib.loads((USB_OC / cfg_file).read_bytes())

        for drv in cfg["UEFI"]["Drivers"]:
            if not drv.get("Enabled"):
                continue
            dpath = USB_OC / "Drivers" / drv["Path"]
            assert dpath.is_file(), f"Missing UEFI driver: {dpath}"
            assert dpath.read_bytes()[:2] == b"MZ", f"Invalid PE32+ MZ header in {dpath}"

        enabled_kexts = []
        for k in cfg["Kernel"]["Add"]:
            if not k.get("Enabled"):
                continue
            bpath = k["BundlePath"]
            enabled_kexts.append(bpath)
            kdir = USB_OC / "Kexts" / bpath
            assert kdir.is_dir(), f"Missing Kext directory on USB: {kdir}"

            plist_path = kdir / k["PlistPath"]
            assert plist_path.is_file(), f"Missing Info.plist: {plist_path}"
            info = plistlib.loads(plist_path.read_bytes())
            assert "CFBundleIdentifier" in info

            if k.get("ExecutablePath"):
                exec_path = kdir / k["ExecutablePath"]
                assert exec_path.is_file(), f"Missing Mach-O executable: {exec_path}"
                magic = exec_path.read_bytes()[:4]
                assert magic in MACHO_MAGICS, f"Invalid Mach-O magic {magic.hex()} in {exec_path}"

        # Verify dependency ordering
        assert enabled_kexts[0] == "Lilu.kext", "Lilu.kext must be loaded first"
        assert enabled_kexts.index("VirtualSMC.kext") < enabled_kexts.index("SMCBatteryManager.kext")
        assert enabled_kexts.index("VirtualSMC.kext") < enabled_kexts.index("SMCProcessor.kext")
        assert enabled_kexts.index("USBToolBox.kext") < enabled_kexts.index("UTBMap.kext")
        assert enabled_kexts.index("VoodooI2C.kext/Contents/PlugIns/VoodooI2CServices.kext") < enabled_kexts.index("VoodooI2C.kext")
        assert enabled_kexts.index("VoodooI2C.kext/Contents/PlugIns/VoodooGPIO.kext") < enabled_kexts.index("VoodooI2C.kext")
        assert enabled_kexts.index("VoodooI2C.kext") < enabled_kexts.index("VoodooI2CHID.kext")
        assert enabled_kexts.index("VoodooPS2Controller.kext") < enabled_kexts.index("VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Keyboard.kext")

        # Never enable itlwm.kext and AirportItlwm.kext together
        assert not ("itlwm.kext" in enabled_kexts and "AirportItlwm.kext" in enabled_kexts)


def test_basesystem_dmg_cryptographic_chunklist_sha256_on_usb():
    chunklist_path = USB_ROOT / "com.apple.recovery.boot" / "BaseSystem.chunklist"
    dmg_path = USB_ROOT / "com.apple.recovery.boot" / "BaseSystem.dmg"

    cl = chunklist_path.read_bytes()
    magic, hdr_size, file_ver, chunk_method, sig_method, _pad, chunk_count, chunk_offset, sig_offset = struct.unpack(
        "<IBBBBIQQQ", cl[:36]
    )
    assert magic == 0x4C4B4E43, f"Invalid chunklist magic: {hex(magic)}"
    assert chunk_count > 0

    with dmg_path.open("rb") as f:
        for i in range(chunk_count):
            pos = chunk_offset + i * 36
            chunk_len = struct.unpack("<I", cl[pos : pos + 4])[0]
            expected_sha256 = cl[pos + 4 : pos + 36]
            data = f.read(chunk_len)
            assert len(data) == chunk_len, f"Chunk {i} truncated: got {len(data)}, expected {chunk_len}"
            actual_sha256 = hashlib.sha256(data).digest()
            assert actual_sha256 == expected_sha256, f"SHA-256 mismatch at chunk {i}/{chunk_count} on USB D:!"


def test_usb_bundle_tarball_full_decompression_integrity():
    tar_path = USB_ROOT / "irisxe-tahoe-bundle.tar.gz"
    with tarfile.open(tar_path, "r:gz") as tf:
        names = set(tf.getnames())
        for req in (
            "Hackintosh-XPS13Plus-IrisXe-Tahoe/install.sh",
            "Hackintosh-XPS13Plus-IrisXe-Tahoe/macos/install-macos.sh",
            "Hackintosh-XPS13Plus-IrisXe-Tahoe/macos/patch-mtl17.py",
            "Hackintosh-XPS13Plus-IrisXe-Tahoe/src/NootedGreen/kern_gen11.cpp",
            "Hackintosh-XPS13Plus-IrisXe-Tahoe/src/HookCase/HookCase.cpp",
        ):
            assert req in names, f"Missing {req} inside D:/irisxe-tahoe-bundle.tar.gz"
