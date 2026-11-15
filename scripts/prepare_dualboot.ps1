param(
    [switch]$DryRun,
    [switch]$ShrinkDisk,
    [int]$ShrinkGB = 115,
    [string]$UsbDriveLetter = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$DistEfi = Join-Path $Root "dist\EFI"
$BundleTar = Join-Path $Root "dist\irisxe-tahoe-bundle.tar.gz"
$GuideMd = Join-Path $Root "dist\LEIAME-INSTALACAO.md"

if (-not (Test-Path (Join-Path $DistEfi "OC\config.plist"))) {
    throw "Missing dist\EFI\OC\config.plist. Run python scripts/build_efi.py first."
}
if (-not (Test-Path (Join-Path $DistEfi "OC\config-install.plist"))) {
    throw "Missing dist\EFI\OC\config-install.plist. Run python scripts/build_efi.py first."
}
if (-not (Test-Path $BundleTar)) {
    throw "Missing dist\irisxe-tahoe-bundle.tar.gz. Run python scripts/pack_macos_bundle.py first."
}

$volC = Get-Volume -DriveLetter C
$freeGB = [math]::Round($volC.SizeRemaining / 1GB, 2)
$totalGB = [math]::Round($volC.Size / 1GB, 2)
$targetWindowsGB = [math]::Round($totalGB - $ShrinkGB, 2)

Write-Output "=== Dell Inspiron 15 5510 Dual-Boot Preparation ==="
Write-Output "Volume C: Total = $totalGB GB | Free = $freeGB GB"
Write-Output "Planned macOS APFS allocation = $ShrinkGB GB | Remaining Windows C: = $targetWindowsGB GB"

if ($targetWindowsGB -lt 120) {
    throw "Safety check failed: Windows C: partition would be smaller than 120 GB ($targetWindowsGB GB)."
}

if ($DryRun) {
    Write-Output "DRY-RUN OK: Pre-flight checks passed (EFI, bundle, and disk capacity verified)."
    exit 0
}

if ($ShrinkDisk) {
    $newSizeBytes = [uint64]($volC.Size - ($ShrinkGB * 1GB))
    Write-Output "Shrinking C: to $([math]::Round($newSizeBytes / 1GB, 2)) GB..."
    Resize-Partition -DriveLetter C -Size $newSizeBytes
    Write-Output "Partition C: resized successfully. $ShrinkGB GB is now unallocated for macOS APFS."
}

if ($UsbDriveLetter -ne "") {
    $usbRoot = "$($UsbDriveLetter.TrimEnd(':')):\"
    if (-not (Test-Path $usbRoot)) {
        throw "USB drive $usbRoot not found."
    }
    Write-Output "Staging OpenCore EFI (install mode) and offline bundle to $usbRoot ..."
    $usbEfi = Join-Path $usbRoot "EFI"
    if (Test-Path $usbEfi) {
        Remove-Item -Recurse -Force $usbEfi
    }
    Copy-Item -Recurse -Force $DistEfi $usbEfi
    # Save accelerated config.plist as config-accelerated.plist and activate config-install.plist for initial boot
    Copy-Item -Force (Join-Path $usbEfi "OC\config.plist") (Join-Path $usbEfi "OC\config-accelerated.plist")
    Copy-Item -Force (Join-Path $usbEfi "OC\config-install.plist") (Join-Path $usbEfi "OC\config.plist")
    Copy-Item -Force $BundleTar (Join-Path $usbRoot "irisxe-tahoe-bundle.tar.gz")
    Copy-Item -Force $GuideMd (Join-Path $usbRoot "LEIAME-INSTALACAO.md")
    Write-Output "USB drive $usbRoot staged successfully!"
}
