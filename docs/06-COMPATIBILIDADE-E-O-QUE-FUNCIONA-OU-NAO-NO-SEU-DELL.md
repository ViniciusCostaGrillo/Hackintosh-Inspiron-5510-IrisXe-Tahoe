# 06 — Compatibilidade Completa: O Que Funciona, O Que Não Funciona e Cuidados no Seu Dell Inspiron 15 5510

> **Resumo:** Mapeamento transparente e detalhado de todos os componentes do seu **Dell Inspiron 15 5510** rodando o **macOS Tahoe 26.7.1 (`25G241`)** com o stack `NootedGreen` + `libxedrv v24`.

---

## ✅ 1. O Que Funciona 100% no Seu Dell Inspiron 15 5510

| Componente | Seu Hardware (`VEN:DEV`) | Como Funciona no macOS Tahoe 26.7.1 |
|---|---|---|
| **Processador (CPU)** | Intel Core i5-11320H (4C/8T, Tiger Lake `Model 0x8C`) | **100% Funcional.** Gerenciamento de energia nativo (`SSDT-PLUG.aml`), Turbo Boost até 4,5 GHz e leitura térmica via `SMCSuperIO` / `xe-temp`. Por não ter núcleos híbridos (P+E), não sofre dos bugs de agendamento das gerações 12ª/13ª. |
| **Placa de Vídeo Integrada (iGPU)** | Intel Iris Xe Graphics (`8086:9A49`, 96 EUs, 8 bancos L3) | **Aceleração por Hardware Metal 2 Ativa (1536 MB VRAM).** Interface Liquid Glass a 60 Hz, transparências do Dock/Menus, Chrome/Brave em 4K a 60 fps, decodificação de vídeo H.264/HEVC (`VideoToolbox`) e suporte a Vulkan 1.4 (`MoltenVK`). |
| **Wi-Fi 6** | Intel Wi-Fi 6 AX201 (`8086:A0F0`) | **100% Funcional** via `AirportItlwm.kext` (versão Tahoe) como interface Wi-Fi nativa do macOS. |
| **Bluetooth** | Intel Wireless Bluetooth (`8087:0026` na porta `HS10`) | **100% Funcional** via `IntelBluetoothFirmware.kext` + `BlueToolFixup.kext` + `UTBMap.kext` (porta interna `255`). Conecta fones Bluetooth, mouses e teclados sem fio. |
| **Webcam Interna** | Integrated Webcam (`0C45:6725` na porta `HS06`) | **100% Funcional Nativamente!** Diferente do Dell XPS 13 Plus (que usa câmera MIPI IPU6 incompatível), a webcam do seu Inspiron 5510 é uma câmera UVC USB padrão conectada internamente na porta `HS06`. Funciona no FaceTime, Zoom, Google Meet e Photo Booth. |
| **Touchpad I2C Multi-Touch** | HID-compliant Touchpad (`DELL0B24` em `\_SB.PC00.I2C1.TPD0`) | **100% Funcional** via `VoodooI2C.kext` + `VoodooI2CHID.kext` + `VoodooGPIOTigerLakeLP` + nossa `SSDT-I2C1.aml` compilada sob medida a partir da sua BIOS. Suporta gestos multi-toque nativos do macOS (pinça, rolagem com 2 dedos, Mission Control com 3/4 dedos). |
| **Teclado Interno** | Standard PS/2 Keyboard (`ACPI\DLLK0B24`) | **100% Funcional** via `VoodooPS2Controller.kext` + `VoodooPS2Keyboard.kext`. |
| **Bateria e Carregador** | Dell ACPI Battery (`PNP0C0A`) | **100% Funcional** via `SMCBatteryManager.kext` + `ECEnabler.kext` (porcentagem exata na barra de menus, status de carregamento e ciclos). |
| **Armazenamento NVMe** | ADATA `SM2P41C3` 256 GB (`1CC1:41C3`) | **100% Funcional** em velocidade máxima PCIe NVMe com TRIM nativo. |
| **Portas USB-A e USB-C** | Controladores `8086:A0ED` (`XHCI`) e `8086:9A13` (`TXHC`) | **100% Funcionais** em velocidade USB 2.0 / 3.2 / USB-C com a `UTBMap.kext` gerada sob medida para as portas físicas do seu notebook. |
| **Áudio USB Externo** | `USB PnP Audio Device` (`0C76:161E`) | **100% Funcional Nativamente** (saída de som e entrada de microfone sem precisar de nenhum patch). |
| **Serviços da Apple** | iCloud, App Store, iMessage e FaceTime | **Funcionais** com o SMBIOS único `MacBookPro16,2` que geramos exclusivamente para a sua máquina (`dist/smbios-secret.json`). |

---

## ❌ 2. O Que NÃO Vai Funcionar (Limitações de Hardware e Contornos)

### 2.1. Microfone Interno do Notebook (Intel Smart Sound / DMIC)
* **Por que não funciona:** Nos notebooks Intel de 11ª geração em diante, os microfones digitais embutidos na moldura da tela (DMIC) não são ligados ao chip Realtek de áudio analógico, e sim diretamente ao DSP **Intel Smart Sound Technology (`8086:A0C8`)**. A Apple nunca escreveu driver para o DSP Intel SST no macOS.
* **Como contornar:** Use o seu **`USB PnP Audio Device` (`0C76:161E`)** (que identificamos conectado no seu notebook) ou qualquer fone Bluetooth / headset USB. Neles o microfone funciona 100%.

### 2.2. Suspensão Profunda de Memória (Deep Sleep S3)
* **Por que não funciona:** O driver de protótipo da Apple (`16.0.32`) para a Iris Xe perde o contexto dos registradores de energia (`Render/Media Forcewake`) se o processador entrar em suspensão profunda S3, fazendo a tela voltar preta ao acordar.
* **Como funciona na prática:** Com os scripts `10-pmset-safe.sh` e `install-xe-lid.sh`, quando você **fechar a tampa do notebook**, a tela se apaga imediatamente e o processador reduz o clock para consumo mínimo (`~3W a 5W` em estado S0), voltando instantaneamente ao abrir a tampa.
* **Cuidado importante:** Se for guardar o notebook dentro de uma **mochila fechada** para transporte longo, **desligue o macOS (Shut Down)** em vez de apenas fechar a tampa, para não gastar bateria nem aquecer dentro da mochila.

### 2.3. AirDrop, Handoff e Sidecar Nativos da Apple
* **Por que não funciona:** Os recursos de Continuidade sem fio da Apple exigem chip Broadcom específico + pilha Wi-Fi proprietária da Apple, enquanto seu notebook usa a placa **Intel Wi-Fi 6 AX201**.
* **O que funciona normalmente:** Internet Wi-Fi 6, Bluetooth, **iCloud Drive, iMessage, FaceTime e App Store** funcionam normalmente. Para transferir arquivos sem fio entre o iPhone/Android e o Mac, basta usar o **LocalSend** (gratuito e de código aberto).

### 2.4. Leitor de Impressão Digital no Botão Power (Goodix `27C6:639C`)
* **Por que não funciona para desbloquear a tela do macOS:** O Touch ID do macOS exige o chip físico **Apple T2 / Secure Enclave** soldado na placa-mãe. Nenhum Hackintosh no mundo consegue emular o Secure Enclave para login do macOS.
* **Observação:** Mantivemos a porta USB `HS05` do leitor Goodix ativa no nosso `UTBMap.kext`, caso você queira futuramente usá-lo no Terminal (`sudo` via `libfprint-tod`).

### 2.5. Aplicativos Antigos que Exigem OpenGL Puro ou DRM FairPlay no Safari
* **OpenGL:** A aceleração por hardware do projeto é focada em **Metal 2** (que move 99% do macOS moderno e apps nativos) e **Vulkan 1.4 (`MoltenVK`)**. Aplicativos legados que dependem exclusivamente de OpenGL antigo rodarão via renderizador de software (CPU).
* **DRM (Netflix / Apple TV+):** Para assistir Netflix, Prime Video ou Disney+ em Full HD/4K, basta usar o **Google Chrome, Brave ou Firefox** (que usam Widevine e funcionam 100% com aceleração em 4K a 60 fps).

---

## ⚠️ 3. Pontos de Atenção no Uso Diário

1. **Alto-Falantes Internos (`Realtek ALC236`):**
   * O seu codec interno é o **Realtek ALC236 (`10EC:0236`)**. Nossa EFI já inclui o `AppleALC.kext` configurado com `alcid=11`.
   * Se os alto-falantes internos não saírem som de primeira com `alcid=11`, você pode testar os outros layouts da Dell para o ALC236 mudando o `alcid=` nos `boot-args` para: `3`, `13`, `15`, `54` ou `99`. Enquanto isso, o seu áudio USB (`0C76:161E`) e fones Bluetooth funcionam imediatamente.
2. **Troca de Resolução e Brilho da Tela:**
   * Evite mudar a resolução pelo painel "Telas" dos Ajustes do Sistema (que pode causar piscadas no `WindowServer`). Use sempre o comando `xe-res` no Terminal (`xe-res list`, `xe-res 1920 1080`, `xe-res 1600 900`).
   * Para controlar o brilho da tela com precisão no driver da Iris Xe, use o utilitário `xe-brilho` (pelo Terminal ou barra de atalhos).
3. **Nunca Atualize o macOS pelo "Atualização de Software" sem Checar Antes:**
   * Como o `NootedGreen` e o `patch-mtl17.py` aplicam patches binários exatos nos arquivos do **macOS Tahoe 26.7.1 (`25G241`)**, deixe as atualizações automáticas do macOS **desativadas**. Só atualize para versões futuras do macOS se o repositório `Hackintosh-XPS13Plus-IrisXe-Tahoe` publicar suporte para a nova build.
