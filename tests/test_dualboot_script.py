import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS_SCRIPT = ROOT / "scripts" / "prepare_dualboot.ps1"


def test_powershell_script_dry_run_succeeds():
    assert PS_SCRIPT.is_file()
    res = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PS_SCRIPT),
            "-DryRun",
        ],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Script failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    assert "DRY-RUN OK" in res.stdout


class TestDualBootScript(unittest.TestCase):
    def test_dry_run(self):
        test_powershell_script_dry_run_succeeds()


if __name__ == "__main__":
    unittest.main()
