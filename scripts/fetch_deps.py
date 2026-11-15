import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / "deps"

URLS = {
    "opencore": "https://github.com/acidanthera/OpenCorePkg/releases/download/1.0.8/OpenCore-1.0.8-RELEASE.zip",
    "hfsplus": "https://raw.githubusercontent.com/acidanthera/OcBinaryData/master/Drivers/HfsPlus.efi",
    "applealc": "https://github.com/acidanthera/AppleALC/releases/download/1.9.8/AppleALC-1.9.8-RELEASE.zip",
    "acpica": "https://github.com/open-acpica/acpica/releases/download/20260408/acpica-win-20260408.zip",
    "iasl": "https://github.com/open-acpica/acpica/releases/download/20260408/iasl-win-20260408.zip",
}

REPO_URL = "https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe.git"


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
        shutil.copyfileobj(resp, out)


def fetch_all_deps(deps_dir: Path = DEPS) -> None:
    deps_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clone Hackintosh-XPS13Plus-IrisXe-Tahoe
    repo_dir = deps_dir / "Hackintosh-XPS13Plus-IrisXe-Tahoe"
    if not (repo_dir / "EFI" / "OC" / "config.plist").is_file():
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(repo_dir)],
            check=True,
        )

    # 2. Download OpenCore 1.0.8 RELEASE
    oc_dir = deps_dir / "OpenCore-1.0.8"
    if not (oc_dir / "Utilities" / "ocvalidate" / "ocvalidate.exe").is_file():
        oc_zip = deps_dir / "OpenCore-1.0.8-RELEASE.zip"
        download_file(URLS["opencore"], oc_zip)
        with zipfile.ZipFile(oc_zip, "r") as zf:
            zf.extractall(oc_dir)

    # 3. Download HfsPlus.efi from OcBinaryData
    hfs_path = deps_dir / "OcBinaryData" / "Drivers" / "HfsPlus.efi"
    if not hfs_path.is_file():
        download_file(URLS["hfsplus"], hfs_path)

    # 4. Download AppleALC 1.9.8 RELEASE
    alc_dir = deps_dir / "AppleALC"
    if not (alc_dir / "AppleALC.kext" / "Contents" / "Info.plist").is_file():
        alc_zip = deps_dir / "AppleALC-RELEASE.zip"
        download_file(URLS["applealc"], alc_zip)
        with zipfile.ZipFile(alc_zip, "r") as zf:
            zf.extractall(alc_dir)

    # 5. Download ACPICA Windows binaries (iasl.exe, acpidump.exe)
    acpica_dir = deps_dir / "acpica"
    if not (acpica_dir / "iasl.exe").is_file() or not (acpica_dir / "acpidump.exe").is_file():
        acpica_zip = deps_dir / "acpica-win.zip"
        download_file(URLS["acpica"], acpica_zip)
        with zipfile.ZipFile(acpica_zip, "r") as zf:
            zf.extractall(acpica_dir)
        iasl_zip = deps_dir / "iasl-win.zip"
        download_file(URLS["iasl"], iasl_zip)
        with zipfile.ZipFile(iasl_zip, "r") as zf:
            zf.extractall(acpica_dir)
        for exe in acpica_dir.rglob("*.exe"):
            if exe.parent != acpica_dir:
                shutil.copy2(exe, acpica_dir / exe.name)


if __name__ == "__main__":
    fetch_all_deps()
    print("Dependencies fetched successfully.")
