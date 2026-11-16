/*
 * SSDT-I2C1 (Dell Inspiron 15 5510 - Tiger Lake-H35):
 * Baseado em SSDT-XPS-I2C.dsl do repositorio de referencia (JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe).
 * Injeta _ADR estatico em \_SB.PC00.I2C0 (0x00150000) e \_SB.PC00.I2C1 (0x00150001)
 * e expoe _INI/XINI e _CRS/XCRS em \_SB.PC00.I2C1.TPD0 (DELL0B24).
 */
DefinitionBlock ("", "SSDT", 2, "HACK", "I2C1TPD", 0x00002000)
{
    External (_SB_.PC00.I2C0, DeviceObj)
    External (_SB_.PC00.I2C1, DeviceObj)
    External (_SB_.PC00.I2C1.TPD0, DeviceObj)
    External (_SB_.PC00.I2C1.TPD0.XCRS, MethodObj)
    External (_SB_.PC00.I2C1.TPD0.XINI, MethodObj)

    Scope (_SB.PC00.I2C0)
    {
        Name (_ADR, 0x00150000)
    }

    Scope (_SB.PC00.I2C1)
    {
        Name (_ADR, 0x00150001)
    }

    Scope (_SB.PC00.I2C1.TPD0)
    {
        Method (_INI, 0, NotSerialized)
        {
            XINI ()
        }

        Method (_CRS, 0, NotSerialized)
        {
            Return (XCRS ())
        }
    }
}
