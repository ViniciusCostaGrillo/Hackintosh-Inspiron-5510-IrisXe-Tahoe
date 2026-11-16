import copy
import json
import os
import plistlib
import secrets
import shutil
import subprocess
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / "deps"
BASE_REPO = DEPS / "Hackintosh-XPS13Plus-IrisXe-Tahoe"
ACPI_CUSTOM = ROOT / "acpi_custom"
DIST = ROOT / "dist"
DIST_EFI = DIST / "EFI"
DIST_OC = DIST_EFI / "OC"
MACSERIAL = DEPS / "OpenCore-1.0.8" / "Utilities" / "macserial" / "macserial.exe"

ACCEL_BOOT_ARGS = (
    "-v keepsyms=1 debug=0x100 IGLogLevel=3 -ngreentglwithgfx -allow3d "
    "-disablegfxfirmware ngreen-dmc=tgl -ngreenv189 -ngreenkeepefi "
    "-ngreenxefix -ngreenfixbootmode amfi_get_out_of_my_way=1 "
    "ngreenSched=4 ngreenV142=3 gfxrst=1 ngreenpm=22 alcid=11"
)

INSTALL_BOOT_ARGS = (
    "keepsyms=1 -vi2c-force-polling -v debug=0x100 -igfxvesa"
)


def generate_smbios() -> dict:
    secret_path = DIST / "smbios-secret.json"
    if secret_path.is_file():
        return json.loads(secret_path.read_text(encoding="utf-8"))

    res = subprocess.run(
        [str(MACSERIAL), "-m", "MacBookPro16,2", "-g", "-n", "1"],
        capture_output=True,
        text=True,
        check=True,
    )
    line = res.stdout.strip().splitlines()[0]
    parts = [p.strip() for p in line.split("|")]
    serial, mlb = parts[0], parts[1]
    smbios = {
        "SystemProductName": "MacBookPro16,2",
        "SystemSerialNumber": serial,
        "MLB": mlb,
        "SystemUUID": str(uuid.uuid4()).upper(),
        "ROM": secrets.token_hex(6),
    }
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret_path.write_text(json.dumps(smbios, indent=2), encoding="utf-8")
    return smbios


def configure_plist(cfg: dict, smbios: dict, accelerated: bool) -> dict:
    cfg = copy.deepcopy(cfg)

    # 1. ACPI > Add: replace SSDT-XPS-I2C.aml with SSDT-I2C1.aml and SSDT-PLUG-ALT.aml with SSDT-PLUG.aml
    new_acpi_add = []
    for entry in cfg["ACPI"]["Add"]:
        if entry["Path"] == "SSDT-XPS-I2C.aml":
            new_acpi_add.append(
                {
                    "Comment": "Dell Inspiron 15 5510 I2C0/I2C1 _ADR injection for DELL0B24 touchpad",
                    "Enabled": True,
                    "Path": "SSDT-I2C1.aml",
                }
            )
        elif entry["Path"] == "SSDT-PLUG-ALT.aml":
            new_acpi_add.append(
                {
                    "Comment": "Dell Inspiron 15 5510 XCPM plugin-type=1 on native _SB.PR00",
                    "Enabled": True,
                    "Path": "SSDT-PLUG.aml",
                }
            )
        else:
            new_acpi_add.append(entry)
    cfg["ACPI"]["Add"] = new_acpi_add

    # 2. ACPI > Patch:
    # - Set Count=1 on GPI0 _STA to XSTA so _SB.EPC._STA is NOT renamed (renaming EPC._STA causes EPC._CRS to return 0xFFFFFFFFFFFFFFFF!)
    # - Replace XPS RHUB.HS08 patch with Dell Inspiron 15 5510 RHUB.HS14 patch (fixes AE_NOT_FOUND on _SB.PC00.XHCI.RHUB.HS14)
    keep_patches = []
    for patch in cfg["ACPI"]["Patch"]:
        comment = patch.get("Comment", "")
        if any(tag in comment for tag in ("TPL0", "TPD0", "RHUB.HS08")):
            continue
        patch = copy.deepcopy(patch)
        if "GPI0 _STA to XSTA" in comment:
            patch["Count"] = 1
        keep_patches.append(patch)

    keep_patches.append(
        {
            "Base": "",
            "BaseSkip": 0,
            "Comment": "Dell Inspiron 5510: Scope RHUB.HS14 to RHUB (HS14 is PCH-H conditional)",
            "Count": 1,
            "Enabled": True,
            "Find": bytes.fromhex("104b202f055f53425f50433030584843495248554248533134"),
            "Limit": 0,
            "Mask": b"",
            "OemTableId": b"",
            "Replace": bytes.fromhex("104b202f045f53425f504330305848434952485542a3a3a3a3"),
            "ReplaceMask": b"",
            "Skip": 0,
            "TableLength": 0,
            "TableSignature": bytes.fromhex("44534454"),
        }
    )
    cfg["ACPI"]["Patch"] = keep_patches

    # 3. DeviceProperties > Add: Native 8086:9A49 Iris Xe on GFX0 in accelerated mode;
    # in install mode (-wegnoigpu), remove PciRoot(0x0)/Pci(0x2,0x0) so WhateverGreen disables IGPU cleanly
    if accelerated:
        cfg["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"] = {
            "AAPL,ig-platform-id": bytes.fromhex("0000499A"),
            "AAPL,slot-name": "built-in",
            "built-in": bytes.fromhex("00"),
            "complete-modeset": bytes.fromhex("01000000"),
            "device-id": bytes.fromhex("499A0000"),
            "enable-max-pixel-clock-override": bytes.fromhex("01000000"),
            "force-online": bytes.fromhex("01000000"),
            "framebuffer-patch-enable": bytes.fromhex("01000000"),
            "hda-gfx": "onboard-1",
            "model": "Intel Iris Xe Graphics",
            "rps-control": bytes.fromhex("01000000"),
        }
    else:
        cfg["DeviceProperties"]["Add"].pop("PciRoot(0x0)/Pci(0x2,0x0)", None)
    cfg["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1F,0x3)"] = {
        "layout-id": (11).to_bytes(4, byteorder="little"),
    }

    # 4. Kernel > Add: remove CpuTopologyRebuild (divides by zero at +6794 when E-Core count is 0!),
    # XHCI-unsupported (hijacks 0xa0ed8086 onto Skylake AppleUSBXHCISPT, preventing XHCI@14000000 from creating ports!),
    # & UTBDefault; add UTBMap & AppleALC; toggle NootedGreen
    new_kexts = []
    for kext in cfg["Kernel"]["Add"]:
        bpath = kext["BundlePath"]
        if bpath in (
            "CpuTopologyRebuild.kext",
            "UTBDefault.kext",
            "XHCI-unsupported.kext",
            "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Mouse.kext",
            "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Trackpad.kext",
        ):
            continue
        if bpath in ("NootedGreen.kext", "AirportItlwm.kext", "BrightnessKeys.kext", "SMCBatteryManager.kext"):
            kext = copy.deepcopy(kext)
            kext["Enabled"] = accelerated
        if bpath == "itlwm.kext":
            kext = copy.deepcopy(kext)
            kext["Enabled"] = not accelerated
        new_kexts.append(kext)
        if bpath == "Lilu.kext":
            new_kexts.append(
                {
                    "Arch": "Any",
                    "BundlePath": "AppleALC.kext",
                    "Comment": "Realtek ALC236 HDA Audio",
                    "Enabled": True,
                    "ExecutablePath": "Contents/MacOS/AppleALC",
                    "MaxKernel": "",
                    "MinKernel": "",
                    "PlistPath": "Contents/Info.plist",
                }
            )
        if bpath == "USBToolBox.kext":
            new_kexts.append(
                {
                    "Arch": "Any",
                    "BundlePath": "UTBMap.kext",
                    "Comment": "Dell Inspiron 15 5510 USB Map (<=15 ports)",
                    "Enabled": True,
                    "ExecutablePath": "",
                    "MaxKernel": "",
                    "MinKernel": "",
                    "PlistPath": "Contents/Info.plist",
                }
            )
    cfg["Kernel"]["Add"] = new_kexts

    # 5. Booter > MmioWhitelist: whitelist Dell Inspiron 15 5510 Tiger Lake runtime MMIO regions
    # (0xC0000000 PCIe ECAM, 0xFD000000 SBREG, 0xFE000000 PMC, 0xFE010000 SPI BAR0, 0xFED00000 HPET/VT-d, 0xFEE00000 LAPIC, 0xFF000000 Flash)
    cfg["Booter"]["MmioWhitelist"] = [
        {"Address": 0xC0000000, "Comment": "PCIe ECAM/MCFG 0xC0000000", "Enabled": True},
        {"Address": 0xFD000000, "Comment": "Tiger Lake PCH SBREG_BAR 0xFD000000", "Enabled": True},
        {"Address": 0xFE000000, "Comment": "Tiger Lake PMC/P2SB MMIO 0xFE000000", "Enabled": True},
        {"Address": 0xFE010000, "Comment": "Tiger Lake SPI BAR0 Runtime NVRAM 0xFE010000", "Enabled": True},
        {"Address": 0xFED00000, "Comment": "HPET / IOAPIC / VT-d 0xFED00000", "Enabled": True},
        {"Address": 0xFEE00000, "Comment": "Local APIC 0xFEE00000", "Enabled": True},
        {"Address": 0xFF000000, "Comment": "System Firmware Flash ROM 0xFF000000", "Enabled": True},
    ]

    # 6. Kernel > Quirks & Emulate:
    # - DisableIoMapper = True because Dell Inspiron 15 5510 DMAR table contains a Reserved Memory Region (RMRR 0x6C000000..0x707FFFFF)
    # - Comet Lake CPUID (0x000A0655) + EBX[23:16]=0x80 (128 logical_per_package)
    cfg["Kernel"]["Quirks"]["DisableIoMapper"] = True
    cfg["Kernel"]["Emulate"]["Cpuid1Data"] = bytes.fromhex("55060A00000000000000000000000000")
    cfg["Kernel"]["Emulate"]["Cpuid1Mask"] = bytes.fromhex("FFFFFFFF000000000000000000000000")

    # 6. Misc > Boot & Debug: Timeout = 5s, HideAuxiliary = False, file logging enabled in install mode
    cfg["Misc"]["Boot"]["Timeout"] = 5
    cfg["Misc"]["Boot"]["HideAuxiliary"] = False
    if not accelerated:
        cfg["Misc"]["Debug"]["AppleDebug"] = True
        cfg["Misc"]["Debug"]["ApplePanic"] = True
        cfg["Misc"]["Debug"]["Target"] = 67

    # 7. NVRAM: CPU name, boot-args, and Delete > boot-args
    oc_vendor_guid = "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"
    boot_guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
    cfg["NVRAM"]["Add"][oc_vendor_guid]["revcpuname"] = "11th Gen Intel(R) Core(TM) i5-11320H"
    cfg["NVRAM"]["Add"][boot_guid]["boot-args"] = ACCEL_BOOT_ARGS if accelerated else INSTALL_BOOT_ARGS
    if "boot-args" not in cfg["NVRAM"]["Delete"][boot_guid]:
        cfg["NVRAM"]["Delete"][boot_guid].append("boot-args")

    # 8. PlatformInfo > Generic: populate unique SMBIOS
    generic = cfg["PlatformInfo"]["Generic"]
    generic["SystemProductName"] = smbios["SystemProductName"]
    generic["SystemSerialNumber"] = smbios["SystemSerialNumber"]
    generic["MLB"] = smbios["MLB"]
    generic["SystemUUID"] = smbios["SystemUUID"]
    generic["ROM"] = bytes.fromhex(smbios["ROM"])

    # 9. UEFI > Drivers: enable HfsPlus.efi
    for drv in cfg["UEFI"]["Drivers"]:
        if drv["Path"] == "HfsPlus.efi":
            drv["Enabled"] = True

    return cfg


def build_efi() -> None:
    if DIST_EFI.exists():
        shutil.rmtree(DIST_EFI)
    shutil.copytree(BASE_REPO / "EFI", DIST_EFI)

    # Copy HfsPlus.efi
    shutil.copy2(
        DEPS / "OcBinaryData" / "Drivers" / "HfsPlus.efi",
        DIST_OC / "Drivers" / "HfsPlus.efi",
    )

    # Copy SSDT-I2C1.aml and SSDT-PLUG.aml; remove SSDT-XPS-I2C.aml and SSDT-PLUG-ALT.aml
    shutil.copy2(ACPI_CUSTOM / "SSDT-I2C1.aml", DIST_OC / "ACPI" / "SSDT-I2C1.aml")
    shutil.copy2(ACPI_CUSTOM / "SSDT-PLUG.aml", DIST_OC / "ACPI" / "SSDT-PLUG.aml")
    for old_aml in ("SSDT-XPS-I2C.aml", "SSDT-PLUG-ALT.aml"):
        p = DIST_OC / "ACPI" / old_aml
        if p.exists():
            p.unlink()

    # Copy AppleALC.kext and UTBMap.kext; remove XPS-only UTBDefault.kext
    shutil.copytree(
        DEPS / "AppleALC" / "AppleALC.kext",
        DIST_OC / "Kexts" / "AppleALC.kext",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        ACPI_CUSTOM / "UTBMap.kext",
        DIST_OC / "Kexts" / "UTBMap.kext",
        dirs_exist_ok=True,
    )
    for kext_name in ("CpuTopologyRebuild.kext", "UTBDefault.kext", "XHCI-unsupported.kext"):
        kdir = DIST_OC / "Kexts" / kext_name
        if kdir.exists():
            shutil.rmtree(kdir)

    # Patch VoodooI2C.kext and VoodooGPIO.kext Info.plist to include Tiger Lake-LP IDs (0xa0e88086&0xFFFCFFFF and INT34C5)
    vi2c_plist = DIST_OC / "Kexts" / "VoodooI2C.kext" / "Contents" / "Info.plist"
    vi2c_data = plistlib.loads(vi2c_plist.read_bytes())
    adl_ctrl = vi2c_data["IOKitPersonalities"]["VoodooI2CPCIAlderRaptorLakeController"]
    if "0xa0e88086" not in adl_ctrl["IOPCIMatch"]:
        adl_ctrl["IOPCIMatch"] = "0xa0e88086&0xFFFCFFFF 0x43e88086&0xFFFCFFFF " + adl_ctrl["IOPCIMatch"]
    vi2c_plist.write_bytes(plistlib.dumps(vi2c_data))

    vgpio_plist = DIST_OC / "Kexts" / "VoodooI2C.kext" / "Contents" / "PlugIns" / "VoodooGPIO.kext" / "Contents" / "Info.plist"
    vgpio_data = plistlib.loads(vgpio_plist.read_bytes())
    tgl_gpio = vgpio_data["IOKitPersonalities"]["VoodooGPIOTigerLakeLP"]
    if "INT34C5" not in tgl_gpio["IONameMatch"]:
        tgl_gpio["IONameMatch"] = ["INT34C5", "INT34C6"] + list(tgl_gpio["IONameMatch"])
    vgpio_plist.write_bytes(plistlib.dumps(vgpio_data))

    base_cfg = plistlib.loads((BASE_REPO / "EFI" / "OC" / "config.plist").read_bytes())
    smbios = generate_smbios()

    accel_cfg = configure_plist(base_cfg, smbios, accelerated=True)
    install_cfg = configure_plist(base_cfg, smbios, accelerated=False)

    (DIST_OC / "config.plist").write_bytes(plistlib.dumps(accel_cfg))
    (DIST_OC / "config-install.plist").write_bytes(plistlib.dumps(install_cfg))


if __name__ == "__main__":
    build_efi()
    print("EFI built successfully at dist/EFI.")
