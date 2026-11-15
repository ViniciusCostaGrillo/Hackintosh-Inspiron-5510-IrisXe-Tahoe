import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UTBMAP_INFO = ROOT / "acpi_custom" / "UTBMap.kext" / "Contents" / "Info.plist"


def build_port_entry(port_num: int, usb_connector: int, comment: str) -> dict:
    return {
        "UsbConnector": usb_connector,
        "port": port_num.to_bytes(4, byteorder="little"),
        "Comment": comment,
    }


def build_usbmap() -> None:
    """
    Generates UTBMap.kext for Dell Inspiron 15 5510 (MacBookPro16,2) based on hardware PnP & ACPI discovery:
    1. PCH XHCI (8086:A0ED, \_SB.PC00.XHCI, PCI 00:14.0):
       - HS01 (1): External USB 3.2 Gen 1 Type-A (Right/Left) -> Connector 3
       - HS02 (2): External USB 3.2 Gen 1 Type-A -> Connector 3
       - HS03 (3): External USB Type-C / Type-A -> Connector 3
       - HS04 (4): External USB 3.2 Gen 1 Type-A (Active receiver) -> Connector 3
       - HS05 (5): Internal Goodix MOC Fingerprint (27C6:639C) -> Connector 255
       - HS06 (6): Internal Integrated UVC Webcam (0C45:6725) -> Connector 255
       - HS10 (10): Internal Intel AX201 Bluetooth (8087:0026) -> Connector 255
       - SS01 (13): External USB 3.2 Gen 1 SuperSpeed Port 1 -> Connector 3
       - SS02 (14): External USB 3.2 Gen 1 SuperSpeed Port 2 -> Connector 3
       - SS03 (15): External USB 3.2 Gen 1 SuperSpeed Port 3 -> Connector 3
       - SS04 (16): External USB 3.2 Gen 1 SuperSpeed Port 4 -> Connector 3
       Total PCH ports mapped = 11 (<= 15 limit).
    2. CPU Thunderbolt/USB4 XHCI (8086:9A13, \_SB.PC00.TXHC, PCI 00:0D.0):
       - HS01 (1): USB-C / Thunderbolt 4 Companion USB2 -> Connector 9
       - SS01 (5): USB-C / Thunderbolt 4 SuperSpeed -> Connector 9
       - SS02 (6): USB-C / Thunderbolt 4 SuperSpeed Alt -> Connector 9
       Total TXHC ports mapped = 3 (<= 15 limit).
    """
    UTBMAP_INFO.parent.mkdir(parents=True, exist_ok=True)

    xhci_ports = {
        "HS01": build_port_entry(1, 3, "External USB-A Port 1 (2.0)"),
        "HS02": build_port_entry(2, 3, "External USB-A Port 2 (2.0)"),
        "HS03": build_port_entry(3, 3, "External USB Port 3 (2.0)"),
        "HS04": build_port_entry(4, 3, "External USB-A Port 4 (2.0)"),
        "HS05": build_port_entry(5, 255, "Internal Goodix Fingerprint (27C6:639C)"),
        "HS06": build_port_entry(6, 255, "Internal Integrated UVC Webcam (0C45:6725)"),
        "HS10": build_port_entry(10, 255, "Internal Intel AX201 Bluetooth (8087:0026)"),
        "SS01": build_port_entry(13, 3, "External USB-A Port 1 (3.0)"),
        "SS02": build_port_entry(14, 3, "External USB-A Port 2 (3.0)"),
        "SS03": build_port_entry(15, 3, "External USB Port 3 (3.0)"),
        "SS04": build_port_entry(16, 3, "External USB-A Port 4 (3.0)"),
    }

    txhc_ports = {
        "HS01": build_port_entry(1, 9, "Thunderbolt 4 / USB-C Companion"),
        "SS01": build_port_entry(5, 9, "Thunderbolt 4 / USB-C SuperSpeed 1"),
        "SS02": build_port_entry(6, 9, "Thunderbolt 4 / USB-C SuperSpeed 2"),
    }

    info_plist = {
        "CFBundleDevelopmentRegion": "English",
        "CFBundleGetInfoString": "v1.0 Dell Inspiron 15 5510 USB Map",
        "CFBundleIdentifier": "com.dortania.USBToolBox.map",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": "UTBMap",
        "CFBundlePackageType": "KEXT",
        "CFBundleShortVersionString": "1.0",
        "CFBundleSignature": "????",
        "CFBundleVersion": "1.0",
        "IOKitPersonalities": {
            "Inspiron5510_PCH_XHCI": {
                "CFBundleIdentifier": "com.dortania.USBToolBox",
                "IOClass": "USBToolBox",
                "IOMatchCategory": "USBToolBox",
                "IOPCIMatch": "0xA0ED8086",
                "IOProviderClass": "AppleUSBXHCI",
                "model": "MacBookPro16,2",
                "IOProviderMergeProperties": {
                    "port-count": (16).to_bytes(4, byteorder="little"),
                    "ports": xhci_ports,
                },
            },
            "Inspiron5510_CPU_TXHC": {
                "CFBundleIdentifier": "com.dortania.USBToolBox",
                "IOClass": "USBToolBox",
                "IOMatchCategory": "USBToolBox",
                "IOPCIMatch": "0x9A138086",
                "IOProviderClass": "AppleUSBXHCI",
                "model": "MacBookPro16,2",
                "IOProviderMergeProperties": {
                    "port-count": (6).to_bytes(4, byteorder="little"),
                    "ports": txhc_ports,
                },
            },
        },
        "OSBundleLibraries": {
            "com.dortania.USBToolBox": "1.0.0",
        },
        "OSBundleRequired": "Root",
    }

    UTBMAP_INFO.write_bytes(plistlib.dumps(info_plist))


if __name__ == "__main__":
    build_usbmap()
    print("UTBMap.kext generated successfully.")
