import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ssdt_i2c1_compiled_and_clean():
    dsl_path = ROOT / "acpi_custom" / "SSDT-I2C1.dsl"
    aml_path = ROOT / "acpi_custom" / "SSDT-I2C1.aml"
    assert dsl_path.is_file()
    assert aml_path.is_file() and aml_path.stat().st_size > 64
    dsl_text = dsl_path.read_text(encoding="utf-8")
    assert "_SB.PC00.I2C1.TPD0" in dsl_text
    assert "TPL0" not in dsl_text


class TestAcpi(unittest.TestCase):
    def test_acpi(self):
        test_ssdt_i2c1_compiled_and_clean()


if __name__ == "__main__":
    unittest.main()
