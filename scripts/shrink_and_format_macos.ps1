$ErrorActionPreference = "Stop"
$LogFile = "C:\Users\Vinic\.gemini\antigravity\scratch\hackintosh-inspiron5510\dist\shrink_disk.log"

try {
    "=== Starting Dual-Boot Partitioning ($(Get-Date)) ===" | Set-Content -Path $LogFile -Encoding UTF8
    $existingMac = Get-Volume | Where-Object { $_.FileSystemLabel -eq "MACOS" }
    if ($existingMac) {
        "MACOS volume already exists ($($existingMac.Size / 1GB) GiB). Skipping shrink." | Add-Content -Path $LogFile
        exit 0
    }

    $volC = Get-Volume -DriveLetter C
    $shrinkBytes = [uint64](115 * 1GB)
    $newSizeBytes = [uint64]($volC.Size - $shrinkBytes)

    "Shrinking C: from $([math]::Round($volC.Size / 1GB, 2)) GiB to $([math]::Round($newSizeBytes / 1GB, 2)) GiB..." | Add-Content -Path $LogFile
    Resize-Partition -DriveLetter C -Size $newSizeBytes

    "Creating MACOS (exFAT) partition in the unallocated space..." | Add-Content -Path $LogFile
    $newPart = New-Partition -DiskNumber 0 -UseMaximumSize -AssignDriveLetter
    Format-Volume -Partition $newPart -FileSystem exFAT -NewFileSystemLabel "MACOS" -Confirm:$false | Out-Null

    "SUCCESS: Partition MACOS created on DriveLetter $($newPart.DriveLetter):" | Add-Content -Path $LogFile
} catch {
    "ERROR: $($_.Exception.Message)" | Add-Content -Path $LogFile
    exit 1
}
