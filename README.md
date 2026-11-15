# 💻 Hackintosh — Dell Inspiron 15 5510 (Intel Iris Xe `8086:9A49` Metal 2 + macOS Tahoe 26.7.1)

![OpenCore](https://img.shields.io/badge/OpenCore-1.0.8-blue?style=for-the-badge)
![macOS](https://img.shields.io/badge/macOS_Tahoe-26.7.1_(25G241)-black?style=for-the-badge&logo=apple)
![GPU](https://img.shields.io/badge/Intel_Iris_Xe-8086:9A49_(96_EU_Metal_2)-0071C5?style=for-the-badge&logo=intel)
![Tests](https://img.shields.io/badge/Pytest_&_ocvalidate-Passing-success?style=for-the-badge)

Repositório completo de engenharia, automação, EFI OpenCore 1.0.8 e drivers de aceleração gráfica **Metal 2** para o notebook **Dell Inspiron 15 5510** (11ª Geração Intel Tiger Lake Core i5-11320H + Intel Iris Xe Graphics `8086:9A49` 96 EU) rodando o **macOS Tahoe 26.7.1 (build `25G241`)** em Dual-Boot com o Windows 11.

> **Baseado em:** [`JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe`](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe) e [`sgiammori/NootedGreen`](https://github.com/sgiammori/NootedGreen), adaptado especificamente para a arquitetura ACPI (`SSDT-I2C1.aml`), topologia de CPU homogênea (`Model 0x8C`, 4C/8T) e controladores USB/Thunderbolt (`UTBMap.kext`) do **Dell Inspiron 15 5510**.

---

## 📚 Documentação Completa do Projeto (Pasta `docs/`)

Toda a história do projeto, decisões de arquitetura, especificações extraídas do hardware, matriz de compatibilidade e manuais passo a passo estão disponíveis na pasta [`docs/`](./docs/):

1. 📄 **[00 — Índice Geral, Histórico da Conversa e Decisões](./docs/00-INDICE-GERAL-E-HISTORICO-DA-CONVERSA.md)**
2. 🔍 **[01 — Especificações do Hardware e Mapeamento PCI/ACPI/USB](./docs/01-ESPECIFICACOES-DO-SEU-HARDWARE-E-MAPEAMENTO.md)**
3. 🏗️ **[02 — Design Técnico e Arquitetura do Projeto](./docs/02-DESIGN-E-ARQUITETURA-DO-PROJETO.md)**
4. ⚙️ **[03 — Plano de Implementação e Automação Executada](./docs/03-PLANO-DE-IMPLEMENTACAO-E-O-QUE-FOI-FEITO.md)**
5. 🚀 **[04 — Passo a Passo Completo de Instalação (BIOS → Boot → macOS)](./docs/04-PASSO-A-PASSO-COMPLETO-DO-QUE-VOCE-VAI-FAZER.md)**
6. ⚡ **[05 — Passo a Passo Exclusivo: Ativação da Placa Intel Iris Xe (Metal 2)](./docs/05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md)**
7. ✅ **[06 — Compatibilidade: O Que Funciona, Limitações e Contornos no Dell 5510](./docs/06-COMPATIBILIDADE-E-O-QUE-FUNCIONA-OU-NAO-NO-SEU-DELL.md)**

---

## 🖥️ Especificações do Dell Inspiron 15 5510

| Componente | Especificação / Modelo | ID de Hardware (`VEN:DEV`) | Caminho ACPI / Barramento |
|---|---|---|---|
| **Processador (CPU)** | 11th Gen Intel Core i5-11320H (4C/8T, até 4.5 GHz) | `Family 6 Model 140 Stepping 2` (`0x8C`) | Tiger Lake-UP3/H35 Silicon |
| **Gráficos (iGPU)** | **Intel Iris Xe Graphics** (96 EUs, 8 bancos L3) | `PCI\VEN_8086&DEV_9A49` | `\_SB.PC00.GFX0` (`PciRoot(0x0)/Pci(0x2,0x0)`) |
| **Armazenamento** | SSD NVMe ADATA `SM2P41C3` 256 GB | `PCI\VEN_1CC1&DEV_41C3` | Standard NVM Express Controller |
| **Wi-Fi 6** | Intel Wi-Fi 6 AX201 (160 MHz, CNVi) | `PCI\VEN_8086&DEV_A0F0` | `\_SB.PC00.CNVW` |
| **Bluetooth** | Intel Wireless Bluetooth | `USB\VID_8087&PID_0026` | `\_SB.PC00.XHCI.RHUB.HS10` |
| **Webcam Interna** | Integrated UVC Webcam | `USB\VID_0C45&PID_6725` | `\_SB.PC00.XHCI.RHUB.HS06` |
| **Touchpad Precisão** | I2C HID Touchpad (`DELL0B24`) | `ACPI\VEN_DELL&DEV_0B24` | `\_SB.PC00.I2C1.TPD0` (`8086:A0E9` + `INT34C5`) |
| **Teclado** | Standard PS/2 Keyboard | `ACPI\VEN_DLLK&DEV_0B24` | `\_SB.PC00.LPCB.PS2K` |
| **Áudio Interno / USB** | Realtek ALC236 + USB PnP Audio Device | `10EC:0236` / `0C76:161E` | `\_SB.PC00.HDAS` (`8086:A0C8`) / USB |
| **Controladores USB** | Intel PCH USB 3.2 (`XHCI`) + Thunderbolt (`TXHC`) | `8086:A0ED` / `8086:9A13` | `\_SB.PC00.XHCI` / `\_SB.PC00.TXHC` |

---

## 📊 Status de Compatibilidade no macOS Tahoe 26.7.1 (`25G241`)

| Recurso | Status | Detalhes / Driver Utilizado |
|---|---|---|
| **Aceleração Gráfica Metal 2 (Iris Xe `8086:9A49`)** | ✅ **100% Funcional** | 1536 MB VRAM, 60 Hz, Liquid Glass, H.264/HEVC `VideoToolbox`, Vulkan 1.4 (`MoltenVK`) via `GPUDriversIntel 16.0.32` + `NootedGreen.kext` + `libxedrv.dylib` (v24) |
| **Gerenciamento de CPU e Energia** | ✅ **100% Funcional** | `SSDT-PLUG-ALT.aml` + `VirtualSMC` (sem `CpuTopologyRebuild`, pois o i5-11320H é 4C/8T homogêneo) |
| **Wi-Fi 6 (AX201) e Bluetooth** | ✅ **100% Funcional** | `AirportItlwm.kext` (Tahoe) + `IntelBluetoothFirmware.kext` + `BlueToolFixup.kext` |
| **Webcam Integrada (`HS06`)** | ✅ **100% Funcional** | Câmera UVC nativa mapeada em `HS06` na `UTBMap.kext` |
| **Touchpad I2C Multi-Touch (`DELL0B24`)** | ✅ **100% Funcional** | `SSDT-I2C1.aml` customizada + `VoodooI2C.kext` + `VoodooI2CHID.kext` (`VoodooGPIOTigerLakeLP`) |
| **Teclado PS/2 e Bateria** | ✅ **100% Funcional** | `VoodooPS2Controller.kext` + `SMCBatteryManager.kext` + `ECEnabler.kext` |
| **Portas USB-A, USB-C e NVMe** | ✅ **100% Funcional** | `UTBMap.kext` sob medida (11 portas em `XHCI` + 3 portas em `TXHC`) |
| **Áudio USB Externo / Alto-Falantes** | ✅ **Funcional** | Áudio USB (`0C76:161E`) 100% nativo; `AppleALC.kext` (`alcid=11`) para Realtek ALC236 |
| **Microfone Interno Digital (DMIC)** | ❌ **Não suportado** | Ligado ao DSP Intel Smart Sound (`8086:A0C8`). **Contorno:** Usar microfone USB ou fone Bluetooth |
| **Suspensão Profunda (Deep Sleep S3)** | ⚠️ **Parcial (S0 Idle)** | Fechar a tampa apaga a tela via `xe-lid` (~3-5W em S0). Desligar antes de guardar em mochila fechada |

---

## ⚡ Guia Rápido: Ativação da Intel Iris Xe (`8086:9A49`) Pós-Instalação

1. **Durante a instalação do macOS Tahoe 26.7.1 (`25G241`):**
   * Use o `EFI/OC/config-install.plist` copiado como `EFI/OC/config.plist` (modo VESA seguro `-igfxvesa` com `NootedGreen.kext` desativada).
2. **Após chegar na Área de Trabalho do macOS Tahoe 26.7.1 (`25G241`):**
   Abra o Terminal e execute:
   ```zsh
   # Opção A: Clonar direto deste repositório no macOS (em ~/xe):
   mkdir -p ~/xe && cd ~/xe
   git clone https://github.com/ViniciusCostaGrillo/Hackintosh-Inspiron-5510-IrisXe-Tahoe.git
   cd Hackintosh-Inspiron-5510-IrisXe-Tahoe

   # Opção B: Ou extrair o bundle offline do pendrive:
   # mkdir -p ~/xe && tar -xzf /Volumes/HACKINTOSH/irisxe-tahoe-bundle.tar.gz -C ~/xe && cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe

   # 1. Instalar Command Line Tools:
   xcode-select --install

   # 2. Compilar e instalar NootedGreen + HookCase + libxedrv v24 + Metal Shader Bridge:
   zsh install.sh

   # 3. Copiar NootedGreen.kext compilada e ativar o config-accelerated.plist no pendrive:
   cp -R build/NootedGreen.kext /Volumes/HACKINTOSH/EFI/OC/Kexts/
   cp /Volumes/HACKINTOSH/EFI/OC/config-accelerated.plist /Volumes/HACKINTOSH/EFI/OC/config.plist
   sync
   ```
3. Autorize as extensões em **Ajustes do Sistema > Privacidade e Segurança > Permitir (Allow)** e reinicie!

👉 Veja o manual detalhado em **[`docs/05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md`](./docs/05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md)**.

---

## 🛠️ Estrutura de Automação e Engenharia deste Repositório

```text
├── EFI/                         # OpenCore 1.0.8 pronto para o Dell Inspiron 15 5510
│   ├── BOOT/BOOTx64.efi
│   └── OC/
│       ├── ACPI/SSDT-I2C1.aml   # SSDT compilada para o Touchpad DELL0B24 em \_SB.PC00.I2C1.TPD0
│       ├── Kexts/UTBMap.kext    # Mapa USB sob medida (XHCI 8086:A0ED + TXHC 8086:9A13)
│       ├── config.plist         # Config com aceleração Metal 2 ativa (-ngreentglwithgfx)
│       └── config-install.plist # Config segura em modo VESA (-igfxvesa) para o instalador
├── acpi_custom/                 # Código-fonte ASL (SSDT-I2C1.dsl) e UTBMap.kext gerados
├── scripts/                     # Pipeline de automação em Python e PowerShell
│   ├── fetch_deps.py            # Baixa OpenCore 1.0.8, OcBinaryData, AppleALC e ACPICA
│   ├── build_acpi.py            # Extrai DSDT da BIOS e compila SSDT-I2C1.aml com iasl.exe
│   ├── build_usbmap.py          # Gera o UTBMap.kext para MacBookPro16,2
│   ├── build_efi.py             # Monta a árvore EFI, gera SMBIOS único e valida com ocvalidate.exe
│   ├── pack_macos_bundle.py     # Empacota o bundle offline .tar.gz protegendo contra AppleDouble (._)
│   └── prepare_dualboot.ps1     # Script seguro de particionamento Dual-Boot e montagem do pendrive
├── tests/                       # Suíte automatizada de testes (pytest) validando ACPI, USB, EFI e Bundle
├── src/ & macos/ & patches/     # Código-fonte do NootedGreen, HookCase, libxedrv v24 e patch-mtl17.py
├── tools/                       # Utilitários pós-instalação (xe-res, xe-brilho, xe-lid, xe-temp)
└── docs/                        # Toda a documentação técnica e manuais passo a passo (00 a 06)
```

> 🔐 **Nota de Segurança sobre SMBIOS:** Os arquivos `EFI/OC/config*.plist` publicados neste repositório possuem valores de exemplo (`CHANGE_ME_SERIAL`) em `PlatformInfo > Generic`. Para gerar números de série únicos localmente na sua máquina, execute `python scripts/build_efi.py` (o arquivo real `dist/smbios-secret.json` é ignorado pelo `.gitignore`).

---

## 🙏 Créditos e Agradecimentos

* **[JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe)** — Desenvolvimento do `libxedrv.dylib` (v24), `patch-mtl17.py`, ponte de shaders LLVM e integração com o macOS Tahoe 26.7.1 (`25G241`).
* **[sgiammori/NootedGreen](https://github.com/sgiammori/NootedGreen)** — Pesquisa original e engenharia reversa dos drivers `GPUDriversIntel 16.0.32` da Apple.
* **[Acidanthera](https://github.com/acidanthera)** — OpenCorePkg, Lilu, VirtualSMC, WhateverGreen, AppleALC e VoodooPS2.
* **[VoodooI2C](https://github.com/VoodooI2C/VoodooI2C)** & **[OpenIntelWireless](https://github.com/OpenIntelWireless)** — Suporte a Touchpad I2C Tiger Lake e Wi-Fi/Bluetooth Intel.
