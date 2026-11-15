/*
 * SSDT-I2C1 (Dell Inspiron 15 5510 - Tiger Lake-H35):
 * Habilita o touchpad I2C HID (DELL0B24) em \_SB.PC00.I2C1.TPD0 usando os recursos originais
 * do firmware (GpioInt no \_SB.GPI0 / INT34C5 atendido pelo VoodooGPIOTigerLakeLP).
 * Os metodos _INI e _CRS originais de TPD0 sao renomeados para XINI/XCRS no config.plist.
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
