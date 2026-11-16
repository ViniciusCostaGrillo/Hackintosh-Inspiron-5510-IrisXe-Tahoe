/*
 * Dell Inspiron 15 5510 XCPM Power Management Injection
 * Attaches plugin-type = 1 to the native BIOS Processor (\_SB.PR00) object
 * without creating duplicate C000..C00F Processor objects.
 */
DefinitionBlock ("", "SSDT", 2, "HACK", "CpuPlug", 0x00003000)
{
    External (\_SB_.PR00, ProcessorObj)

    Scope (\_SB.PR00)
    {
        Method (_DSM, 4, NotSerialized)
        {
            If ((Arg2 == Zero))
            {
                Return (Buffer (One)
                {
                     0x03
                })
            }

            Return (Package (0x02)
            {
                "plugin-type",
                One
            })
        }
    }
}
