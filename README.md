# 💻 Hackintosh — Dell Inspiron 15 5510 (Intel Iris Xe `8086:9A49` Metal + macOS Tahoe 26.7.1)

![OpenCore](https://img.shields.io/badge/OpenCore-1.0.8-blue?style=for-the-badge)
![macOS](https://img.shields.io/badge/macOS_Tahoe-26.7.1_(25G241)-black?style=for-the-badge&logo=apple)
![GPU](https://img.shields.io/badge/Intel_Iris_Xe-8086:9A49_(96_EU_Metal)-0071C5?style=for-the-badge&logo=intel)
![Tests](https://img.shields.io/badge/Pytest_&_ocvalidate-Passing-success?style=for-the-badge)
![Boot](https://img.shields.io/badge/macOS_Recovery-Verified_Working-brightgreen?style=for-the-badge)

Repositório completo de engenharia, automação, EFI OpenCore 1.0.8 e drivers de aceleração gráfica **Metal** para o notebook **Dell Inspiron 15 5510** (11ª Geração Intel Tiger Lake Core i5-11320H + Intel Iris Xe Graphics `8086:9A49` 96 EU) rodando o **macOS Tahoe 26.7.1 (build `25G241`)** em Dual-Boot com o Windows 11.

> **Status de Boot:** ✅ **Testado e Aprovado!** O instalador do macOS inicializa perfeitamente no Dell Inspiron 15 5510 após a resolução do freeze em `libignition` / `launchd` via spoof Comet Lake 4-core e estabilização do SSD NVMe ADATA SM2P41C3 via `NVMeFix`.

---

## 📚 Documentação Completa do Projeto (Pasta `docs/`)

Toda a história do projeto, decisões de arquitetura, especificações extraídas do hardware, matriz de compatibilidade e manuais passo a passo estão disponíveis na pasta [`docs/`](./docs/):

1. 📄 **[00 — Índice Geral, Histórico da Conversa e Decisões](./docs/00-INDICE-GERAL-E-HISTORICO-DA-CONVERSA.md)**
2. 🔍 **[01 — Especificações do Hardware e Mapeamento PCI/ACPI/USB](./docs/01-ESPECIFICACOES-DO-SEU-HARDWARE-E-MAPEAMENTO.md)**
3. 🏗️ **[02 — Design Técnico e Arquitetura do Projeto](./docs/02-DESIGN-E-ARQUITETURA-DO-PROJETO.md)**
4. ⚙️ **[03 — Plano de Implementação e Automação Executada](./docs/03-PLANO-DE-IMPLEMENTACAO-E-O-QUE-FOI-FEITO.md)**
5. 🚀 **[04 — Passo a Passo Completo de Instalação (BIOS → Boot → macOS)](./docs/04-PASSO-A-PASSO-COMPLETO-DO-QUE-VOCE-VAI-FAZER.md)**
6. ⚡ **[05 — Passo a Passo Exclusivo: Ativação da Placa Intel Iris Xe (Metal)](./docs/05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md)**
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

## ⚡ Guia Rápido: Instalação e Ativação Metal Pós-Instalação

### Fase 1: Instalação Segura do macOS
1. O pendrive utiliza `EFI/OC/config-install.plist` (copiado como `config.plist`), operando em modo VESA seguro com WhateverGreen (`-igfxvesa`), CPUID Spoof Comet Lake limpo (`55060A00 00000000 00000000 00000000`) e `NVMeFix.kext`.
2. Conecte-se à internet na Recuperação via USB Tethering (Samsung Galaxy A55 ou Android) ou `itlwm.kext`.
3. No Utilitário de Disco, formate a partição `MACOS` como **APFS** com o nome `Macintosh HD`.
4. Instale o macOS Tahoe e aguarde as reinicializações até chegar à Área de Trabalho.

### Fase 2: Ativação da Intel Iris Xe Metal Pós-Instalação

Oferecemos duas abordagens completas no repositório:

#### Opção A (Recomendada / 1-Clique): WhateverXe (por b00t0x)
1. No macOS, abra o pendrive `HACKINTOSH` e instale o pacote gráfico:
   ```zsh
   sudo installer -pkg /Volumes/HACKINTOSH/WhateverXe-Graphics-0.4.4.pkg -target /
   ```
2. Ative a configuração correspondente no pendrive:
   ```zsh
   cp /Volumes/HACKINTOSH/EFI/OC/config-whateverxe.plist /Volumes/HACKINTOSH/EFI/OC/config.plist
   sync
   ```
3. Autorize as extensões em **Ajustes do Sistema > Privacidade e Segurança** e reinicie!

#### Opção B (Stack Apple 16.0.32 Prototype): NootedGreen (por JulioNectar)
1. Extraia o pacote offline em `~/xe` e compile a stack:
   ```zsh
   mkdir -p ~/xe
   tar -xzf /Volumes/HACKINTOSH/irisxe-tahoe-bundle.tar.gz -C ~/xe
   cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe
   xcode-select --install
   zsh install.sh
   ```
2. Ative o `config-nootedgreen.plist` e reinicie.

👉 Veja o manual completo em **[`docs/05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md`](./docs/05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md)**.

---

## 🛠️ Estrutura do Repositório

```text
├── EFI/
│   ├── BOOT/BOOTx64.efi
│   └── OC/
│       ├── ACPI/SSDT-I2C1.aml          # Touchpad DELL0B24 em \_SB.PC00.I2C1.TPD0
│       ├── Kexts/
│       │   ├── WhateverXe.kext         # Driver Lilu para Intel Iris Xe (b00t0x)
│       │   ├── AMFIPass.kext           # Compatibilidade AMFI para drivers de vídeo
│       │   ├── WhateverGreen.kext      # Modo VESA seguro durante instalação
│       │   ├── NootedGreen.kext        # Driver alternativo stack Apple 16.0.32
│       │   ├── NVMeFix.kext            # Estabilização do SSD ADATA SM2P41C3
│       │   └── UTBMap.kext             # Mapeamento USB sob medida (Dell Inspiron 5510)
│       ├── config-install.plist        # Configuração validada para o instalador (-igfxvesa)
│       ├── config-whateverxe.plist     # Configuração pós-instalação WhateverXe
│       └── config-nootedgreen.plist    # Configuração pós-instalação NootedGreen
├── acpi_custom/                        # Código-fonte ASL (SSDT-I2C1.dsl) e UTBMap.kext
├── scripts/                            # Pipeline de automação (build_efi.py, prepare_dualboot.ps1)
├── tests/                              # Suíte de testes automatizados (pytest e ocvalidate)
└── docs/                               # Manuais detalhados passo a passo (00 a 06)
```

> 🔐 **Nota de Segurança:** Todos os arquivos públicos de configuração utilizam identificadores genéricos (`CHANGE_ME_SERIAL`). O arquivo `build_efi.py` gera números únicos mantidos estritamente locais.

---

## 🙏 Créditos

* **[b00t0x/WhateverXe](https://github.com/b00t0x/WhateverXe)** — Driver Lilu dedicado para aceleração de Intel Iris Xe.
* **[JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe)** — Pesquisa e desenvolvimento do driver prototype Apple Tiger Lake.
* **[sgiammori/NootedGreen](https://github.com/sgiammori/NootedGreen)** — Engenharia reversa dos drivers gráficos da Intel.
* **[Acidanthera](https://github.com/acidanthera)** — OpenCorePkg, Lilu, VirtualSMC, WhateverGreen, AppleALC e VoodooPS2.
* **[OpenIntelWireless](https://github.com/OpenIntelWireless)** — Drivers itlwm e AirportItlwm para placas Intel Wi-Fi 6.
