# 01 — Especificações do Seu Hardware e Mapeamento para o macOS

Este documento registra o levantamento completo de hardware realizado diretamente no seu **Dell Inspiron 15 5510**, incluindo IDs PCI/USB, caminhos ACPI extraídos da sua tabela `DSDT.aml` real (`v02 DELL Dell Inc 00000002`) e como cada componente foi configurado na sua pasta `EFI`.

---

## 1. Resumo Geral do Sistema

* **Fabricante / Modelo:** Dell Inc. — Inspiron 15 5510 (Subsystem ID `1028:0B24`)
* **SMBIOS Configurado no OpenCore:** `MacBookPro16,2`
* **Memória RAM Instalada:** 8 GB DDR4 (`8.316.030.976` bytes) — *Nota: possui dois slots SO-DIMM acessíveis, permitindo upgrade futuro para 16 GB ou 32 GB.*

---

## 2. Processador (CPU) e Gráficos Integrados (iGPU)

| Item | Especificação Real Extraída | Caminho ACPI / PCI | Configuração na Sua EFI |
|---|---|---|---|
| **Processador** | 11th Gen Intel Core i5-11320H @ 3.20GHz (4 núcleos físicos / 8 threads) | `Intel64 Family 6 Model 140 Stepping 2` (`Model 0x8C` — silício Tiger Lake-UP3/H35) | Spoof de CPUID via `Kernel > Emulate` (`Cpuid1Data = 65060A00...`) + gerenciamento de energia via `SSDT-PLUG-ALT.aml`. `CpuTopologyRebuild.kext` foi removido por não haver E-cores. |
| **GPU Integrada** | Intel Iris Xe Graphics (GT2, **96 Execution Units**, 8 bancos L3, Display Engine 12) | `PCI\VEN_8086&DEV_9A49&SUBSYS_0B241028&REV_03` · `\_SB.PC00.GFX0` (`PciRoot(0x0)/Pci(0x2,0x0)`) | **ID Nativo `8086:9A49`** (o mesmo ID do driver Apple `16.0.32`). Na instalação usa `-igfxvesa`; após rodar o `install.sh`, usa `NootedGreen.kext` + `HookCase.kext` + `libxedrv v24` com aceleração **Metal 2**. |

---

## 3. Armazenamento (SSD NVMe) e Layout de Partições

* **Modelo do SSD:** `SM2P41C3 NVMe ADATA 256GB`
* **Controlador PCI:** `PCI\VEN_1CC1&DEV_41C3&SUBSYS_41C31CC1&REV_03` (`Controlador Padrão NVM Express`)
* **Modo de Operação:** **AHCI / NVMe Padrão** (sem Intel VMD / RAID ativo — compatível direto com o macOS sem precisar formatar o Windows!).
* **Kext no OpenCore:** `NVMeFix.kext` ativo.

### Layout de Partições do Disco 0 (GPT — 256 GB / 238,47 GiB):

| Partição | Tipo | Tamanho Atual | Como Fica no Dual-Boot (`prepare_dualboot.ps1`) |
|---|---|---|---|
| **Partição 1** | EFI System Partition (ESP) | **200 MB** | Mantida intacta (já possui os 200 MB exigidos pelo APFS do macOS). |
| **Partição 2** | Microsoft Reserved (MSR) | **16 MB** | Mantida intacta. |
| **Partição 3 (`C:`)** | Windows 11 (NTFS) | **237,41 GiB** (~74,8 GiB em uso / ~162,5 GiB livres) | Reduzida para **122,41 GiB (~131,4 GB decimais)** para o Windows, liberando **115 GiB (~123,5 GB decimais)** para a nova partição **APFS (`Macintosh HD`)**. |
| **Partição 4** | Windows Recovery | **911 MB** | Mantida intacta. |

---

## 4. Rede, Bluetooth, Áudio e Periféricos Internos

| Componente | Hardware Detectado | ID / Caminho ACPI | Como Funciona no macOS Tahoe 26.7.1 |
|---|---|---|---|
| **Wi-Fi 6** | Intel Wi-Fi 6 AX201 160MHz | `PCI\VEN_8086&DEV_A0F0` · `\_SB.PC00.CNVW` | **Funciona nativamente** no menu Wi-Fi do macOS via `AirportItlwm.kext` (build específica para Tahoe 26.x). |
| **Bluetooth** | Intel Wireless Bluetooth (CNVi) | `USB\VID_8087&PID_0026` na porta `HS10` de `\_SB.PC00.XHCI` | **Funciona** via `IntelBluetoothFirmware.kext` + `IntelBTPatcher.kext` + `BlueToolFixup.kext` + porta `HS10` mapeada como interna (`255`). |
| **Webcam Interna** | Integrated Webcam (UVC) | `USB\VID_0C45&PID_6725` na porta `HS06` de `\_SB.PC00.XHCI` | **Funciona nativamente!** Como é uma câmera USB UVC padrão (e não MIPI IPU6), basta o mapeamento da porta `HS06` como interna (`255`) no `UTBMap.kext`. |
| **Touchpad** | Dispositivo HID I2C (`DELL0B24`) | `ACPI\DELL0B24` em `\_SB.PC00.I2C1.TPD0` (`8086:A0E9`) + GPIO `\_SB.GPI0` (`INT34C5`) | **Funciona com gestos Multi-Touch** via `VoodooI2C.kext` (com `VoodooGPIOTigerLakeLP` corrigido) + `VoodooI2CHID.kext` + nossa `SSDT-I2C1.aml`. |
| **Teclado Interno** | Teclado PS/2 + Atalhos de Brilho Dell | ACPI PS/2 | **Funciona** via `VoodooPS2Controller.kext` + `BrightnessKeys.kext`. |
| **Áudio USB Externo** | USB PnP Audio Device | `USB\VID_0C76&PID_161E` | **100% Nativo (Plug-and-Play)** — saída de som e microfone funcionam imediatamente via `AppleUSBAudio`. |
| **Áudio Interno** | Realtek ALC236 + Intel Smart Sound (SST) | `10EC:0236` atrás de `8086:A0C8` (`\_SB.PC00.HDAS`) | Configurado com `AppleALC.kext` (`alcid=11` inicial; alternativos: `3, 13, 15, 54, 99`). *Nota: O microfone interno digital (DMIC) fica preso ao DSP Intel SST, portanto use o microfone do seu dispositivo USB ou fone Bluetooth.* |
| **Leitor Biométrico** | Goodix MOC Fingerprint | `USB\VID_27C6&PID_639C` na porta `HS05` de `\_SB.PC00.XHCI` | Touch ID da Apple exige chip T2/Secure Enclave, mas o repositório inclui utilitário opcional (`tools/fingerprint`) baseado em `libfprint` (`goodixmoc`) para autenticar o comando `sudo` no Terminal. |

---

## 5. Mapa de Portas USB Gerado (`UTBMap.kext`)

O macOS impõe um limite rígido de **15 portas por controlador XHCI**. Nossa `UTBMap.kext` (`dist/EFI/OC/Kexts/UTBMap.kext`) mapeia os dois controladores do seu Dell Inspiron 15 5510 dentro desse limite:

### Controlador 1: Intel PCH USB 3.2 (`8086:A0ED` — `\_SB.PC00.XHCI`, 11 portas mapeadas)
* `HS01` (Porta 1) / `SS01` (Porta 13): Porta USB-A Externa 1 (USB 2.0 / USB 3.0) — Tipo `3`
* `HS02` (Porta 2) / `SS02` (Porta 14): Porta USB-A Externa 2 (USB 2.0 / USB 3.0) — Tipo `3`
* `HS03` (Porta 3) / `SS03` (Porta 15): Porta USB Externa 3 — Tipo `3`
* `HS04` (Porta 4) / `SS04` (Porta 16): Porta USB-A Externa 4 — Tipo `3`
* `HS05` (Porta 5): Leitor Biométrico Interno Goodix (`27C6:639C`) — Tipo `255` (Interno)
* `HS06` (Porta 6): Webcam Integrada UVC (`0C45:6725`) — Tipo `255` (Interno)
* `HS10` (Porta 10): Bluetooth Interno Intel AX201 (`8087:0026`) — Tipo `255` (Interno)

### Controlador 2: Intel Thunderbolt 4 / USB4 XHCI (`8086:9A13` — `\_SB.PC00.TXHC`, 3 portas mapeadas)
* `HS01` (Porta 1): Porta USB-C / Thunderbolt 4 (Companion USB 2.0) — Tipo `9` (Type-C)
* `SS01` (Porta 5) / `SS02` (Porta 6): Porta USB-C / Thunderbolt 4 SuperSpeed — Tipo `9` (Type-C)
