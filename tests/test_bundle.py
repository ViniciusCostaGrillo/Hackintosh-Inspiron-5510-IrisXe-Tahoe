import tarfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "dist" / "irisxe-tahoe-bundle.tar.gz"
GUIDE = ROOT / "dist" / "LEIAME-INSTALACAO.md"


def test_tarball_contains_required_macos_scripts():
    assert BUNDLE.is_file() and BUNDLE.stat().st_size > 1_000_000
    with tarfile.open(BUNDLE, "r:gz") as tf:
        names = set(tf.getnames())
        assert "Hackintosh-XPS13Plus-IrisXe-Tahoe/install.sh" in names
        assert "Hackintosh-XPS13Plus-IrisXe-Tahoe/macos/install-macos.sh" in names
        assert "Hackintosh-XPS13Plus-IrisXe-Tahoe/macos/patch-mtl17.py" in names
    assert GUIDE.is_file()


class TestBundle(unittest.TestCase):
    def test_bundle(self):
        test_tarball_contains_required_macos_scripts()


if __name__ == "__main__":
    unittest.main()
