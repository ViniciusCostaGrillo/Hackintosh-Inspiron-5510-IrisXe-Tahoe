/*
 * SSDT-I2C1 (Dell Inspiron 15 5510 - Tiger Lake-H35):
 * Injeta _ADR estatico em \_SB.PC00.I2C0 (0x00150000) e \_SB.PC00.I2C1 (0x00150001)
 * para que o VoodooI2C anexe ao controlador PCI A0E8/A0E9 e descubra \_SB.PC00.I2C1.TPD0 (DELL0B24)
 * mantendo os metodos _INI e _CRS nativos da BIOS Dell intactos.
 */
DefinitionBlock ("", "SSDT", 2, "HACK", "I2C1TPD", 0x00002000)
{
    External (_SB_.PC00.I2C0, DeviceObj)
    External (_SB_.PC00.I2C1, DeviceObj)
    External (_SB_.PC00.I2C1.TPD0, DeviceObj)

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
        Name (GPIO, One)
    }
}
