import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACPICA = ROOT / "deps" / "acpica"
ACPI_DUMP = ROOT / "acpi_dump"
ACPI_CUSTOM = ROOT / "acpi_custom"


def build_acpi() -> None:
    ACPI_DUMP.mkdir(parents=True, exist_ok=True)
    ACPI_CUSTOM.mkdir(parents=True, exist_ok=True)

    iasl = ACPICA / "iasl.exe"
    acpidump = ACPICA / "acpidump.exe"

    # 1. Dump system DSDT if not already dumped
    dsdt_aml = ACPI_DUMP / "dsdt.dat"
    if acpidump.is_file() and not dsdt_aml.is_file():
        subprocess.run(
            [str(acpidump), "-b", "-n", "DSDT"],
            cwd=str(ACPI_DUMP),
            check=False,
        )
        if dsdt_aml.is_file():
            subprocess.run([str(iasl), "-d", str(dsdt_aml)], cwd=str(ACPI_DUMP), check=False)

    # 2. Compile custom SSDT-I2C1.dsl -> SSDT-I2C1.aml
    dsl_path = ACPI_CUSTOM / "SSDT-I2C1.dsl"
    aml_path = ACPI_CUSTOM / "SSDT-I2C1.aml"
    subprocess.run(
        [str(iasl), "-oa", "-p", str(aml_path.with_suffix("")), str(dsl_path)],
        check=True,
    )
    if not aml_path.is_file():
        raise FileNotFoundError(f"Expected compiled AML at {aml_path}")


if __name__ == "__main__":
    build_acpi()
    print("ACPI tables extracted and SSDT-I2C1.aml compiled successfully.")
