/*
 * Intel ACPI Component Architecture
 * AML/ASL+ Disassembler version 20260408 (32-bit version)
 * Copyright (c) 2000 - 2026 Intel Corporation
 * 
 * Disassembly of C:/Users/Vinic/.gemini/antigravity/scratch/hackintosh-inspiron5510/acpi_custom/DMAR.aml
 *
 * ACPI Data Table [DMAR]
 *
 * Format: [HexOffset DecimalOffset ByteLength]  FieldName : FieldValue (in hex)
 */

[000h 0000 004h]                   Signature : "DMAR"    [DMA Remapping Table]
[004h 0004 004h]                Table Length : 00000080
[008h 0008 001h]                    Revision : 02
[009h 0009 001h]                    Checksum : A3
[00Ah 0010 006h]                      Oem ID : "INTEL "
[010h 0016 008h]                Oem Table ID : "Dell Inc"
[018h 0024 004h]                Oem Revision : 00000002
[01Ch 0028 004h]             Asl Compiler ID : "    "
[020h 0032 004h]       Asl Compiler Revision : 01000013

[024h 0036 001h]          Host Address Width : 26
[025h 0037 001h]                       Flags : 01
[026h 0038 00Ah]                    Reserved : 00 00 00 00 00 00 00 00 00 00

[030h 0048 002h]               Subtable Type : 0000 [Hardware Unit Definition]
[032h 0050 002h]                      Length : 0018

[034h 0052 001h]                       Flags : 00
[035h 0053 001h]        Size (decoded below) : 00
                          Size (pages, log2) : 0
[036h 0054 002h]          PCI Segment Number : 0000
[038h 0056 008h]       Register Base Address : 00000000FED90000

[040h 0064 001h]           Device Scope Type : 01 [PCI Endpoint Device]
[041h 0065 001h]                Entry Length : 08
[042h 0066 001h]                       Flags : 00
[043h 0067 001h]                    Reserved : 00
[044h 0068 001h]              Enumeration ID : 00
[045h 0069 001h]              PCI Bus Number : 00

[046h 0070 002h]                    PCI Path : 02,00


[048h 0072 002h]               Subtable Type : 0000 [Hardware Unit Definition]
[04Ah 0074 002h]                      Length : 0018

[04Ch 0076 001h]                       Flags : 00
[04Dh 0077 001h]        Size (decoded below) : 00
                          Size (pages, log2) : 0
[04Eh 0078 002h]          PCI Segment Number : 0000
[050h 0080 008h]       Register Base Address : 00000000FED84000

[058h 0088 001h]           Device Scope Type : 02 [PCI Bridge Device]
[059h 0089 001h]                Entry Length : 08
[05Ah 0090 001h]                       Flags : 00
[05Bh 0091 001h]                    Reserved : 00
[05Ch 0092 001h]              Enumeration ID : 00
[05Dh 0093 001h]              PCI Bus Number : 00

[05Eh 0094 002h]                    PCI Path : 07,00


[060h 0096 002h]               Subtable Type : 0000 [Hardware Unit Definition]
[062h 0098 002h]                      Length : 0020

[064h 0100 001h]                       Flags : 01
[065h 0101 001h]        Size (decoded below) : 00
                          Size (pages, log2) : 0
[066h 0102 002h]          PCI Segment Number : 0000
[068h 0104 008h]       Register Base Address : 00000000FED91000

[070h 0112 001h]           Device Scope Type : 03 [IOAPIC Device]
[071h 0113 001h]                Entry Length : 08
[072h 0114 001h]                       Flags : 00
[073h 0115 001h]                    Reserved : 00
[074h 0116 001h]              Enumeration ID : 02
[075h 0117 001h]              PCI Bus Number : 00

[076h 0118 002h]                    PCI Path : 1E,07


[078h 0120 001h]           Device Scope Type : 04 [Message-capable HPET Device]
[079h 0121 001h]                Entry Length : 08
[07Ah 0122 001h]                       Flags : 00
[07Bh 0123 001h]                    Reserved : 00
[07Ch 0124 001h]              Enumeration ID : 00
[07Dh 0125 001h]              PCI Bus Number : 00

[07Eh 0126 002h]                    PCI Path : 1E,06


Raw Table Data: Length 128 (0x80)

    0000: 44 4D 41 52 80 00 00 00 02 A3 49 4E 54 45 4C 20  // DMAR......INTEL 
    0010: 44 65 6C 6C 20 49 6E 63 02 00 00 00 20 20 20 20  // Dell Inc....    
    0020: 13 00 00 01 26 01 00 00 00 00 00 00 00 00 00 00  // ....&...........
    0030: 00 00 18 00 00 00 00 00 00 00 D9 FE 00 00 00 00  // ................
    0040: 01 08 00 00 00 00 02 00 00 00 18 00 00 00 00 00  // ................
    0050: 00 40 D8 FE 00 00 00 00 02 08 00 00 00 00 07 00  // .@..............
    0060: 00 00 20 00 01 00 00 00 00 10 D9 FE 00 00 00 00  // .. .............
    0070: 03 08 00 00 02 00 1E 07 04 08 00 00 00 00 1E 06  // ................
