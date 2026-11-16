# 05 — Passo a Passo Exclusivo: Ativação da Placa Gráfica Intel Iris Xe (`8086:9A49` — Metal)

> **Equipamento:** Dell Inspiron 15 5510 — Intel Core i5-11320H (`Family 6 Model 140 / 0x8C`, Tiger Lake-UP3/H35)  
> **GPU:** Intel Iris Xe Graphics (`PCI\VEN_8086&DEV_9A49`, 96 Execution Units, 8 bancos L3, Display Engine 12)  
> **Sistema Alvo:** macOS Tahoe **26.7.1** (Build **`25G241`**)  
> **Módulos Prontos no Pendrive:** `WhateverXe-Graphics-0.4.4.pkg`, `WhateverXe.kext`, `AMFIPass.kext`, `NootedGreen.kext`

---

## 🧠 Por Que a Aceleração Gráfica é Feita no Pós-Instalação?

A Apple nunca comercializou um Mac oficial com processadores Intel de 11ª geração (Tiger Lake) nem com gráficos Intel Iris Xe. Por conta disso:
1. O instalador (`BaseSystem.dmg`) é uma partição montada em modo **somente leitura** (`read-only`).
2. Os drivers que trazem a aceleração Metal da Iris Xe (sejam eles via `WhateverXe` ou `NootedGreen` + `libxedrv`) necessitam residir nas pastas de sistema do macOS: `/Library/GPUBundles` ou `/System/Library/Extensions`.
3. Portanto, o sistema operacional deve primeiro ser instalado em modo gráfico compatível (`WhateverGreen` + `-igfxvesa`). Assim que você entra na Área de Trabalho com o disco `Macintosh HD` gravável, a aceleração Metal é ativada.

---

## 🚀 Método 1 (Recomendado e Mais Rápido): WhateverXe + Pacote PKG Automatizado

O **WhateverXe** (desenvolvido por *b00t0x*) é o driver OpenCore mais moderno para gráficos Intel Iris Xe em arquiteturas Tiger Lake e Alder Lake. Ele gerencia nativamente a compensação da memória de vídeo (DVMT) que a Dell bloqueia na BIOS e injeta a aceleração Metal.

Todos os arquivos já estão no seu pendrive `HACKINTOSH (D:)`!

### Passo 1: Executar o Instalador Gráfico `WhateverXe-Graphics-0.4.4.pkg`
Com o pendrive `HACKINTOSH` plugado no notebook no macOS:

1. Abra o **Finder** e acesse o pendrive **`HACKINTOSH`**.
2. Dê um duplo-clique no arquivo **`WhateverXe-Graphics-0.4.4.pkg`** (ou abra o **Terminal** e rode):
   ```zsh
   sudo installer -pkg /Volumes/HACKINTOSH/WhateverXe-Graphics-0.4.4.pkg -target /
   ```
3. Siga o assistente de instalação do pacote até o final. Ele instalará automaticamente os bundles de aceleração Metal e as bibliotecas da GPU Iris Xe em `/Library/GPUBundles`.

---

### Passo 2: Ativar o `config-whateverxe.plist` no Pendrive
No **Terminal** do macOS, execute o comando abaixo para substituir o arquivo de configuração seguro pelo arquivo com aceleração total da Iris Xe:

```zsh
cp /Volumes/HACKINTOSH/EFI/OC/config-whateverxe.plist /Volumes/HACKINTOSH/EFI/OC/config.plist
sync
```

#### O que essa configuração altera automaticamente:
* **Kexts:** Ativa `WhateverXe.kext` e `AMFIPass.kext`; desativa `WhateverGreen.kext` e `itlwm.kext` (ativa `AirportItlwm.kext`).
* **Boot-Args:** Remove `-igfxvesa` e aplica:
  ```text
  -v keepsyms=1 debug=0x100 -vi2c-force-polling -igfxdvmt amfi_get_out_of_my_way=1 ipc_control_port_options=0 alcid=11
  ```
  *(O argumento `-igfxdvmt` faz o kernel ignorar a limitação de DVMT de 32MB/60MB imposta pela BIOS da Dell).*
* **DeviceProperties (`PciRoot(0x0)/Pci(0x2,0x0)`):**
  * `AAPL,ig-platform-id`: `0000499A` (ID nativo da Tiger Lake Iris Xe 96 EU).
  * `device-id`: `499A0000`.
  * `framebuffer-patch-enable`: `01000000`.
  * `framebuffer-stolenmem`: `0000C003` (aloca 60MB virtuais para o framebuffer).
  * `enable-metal`: `01000000`.

---

### Passo 3: Autorizar as Extensões de Sistema e Reiniciar
1. Vá em **Ajustes do Sistema (System Settings) > Privacidade e Segurança (Privacy & Security)**.
2. Role até a seção "Segurança" e clique em **Permitir (Allow)** para autorizar os novos módulos do sistema.
3. No Terminal, garanta a reconstrução do cache de extensões:
   ```zsh
   sudo kmutil install --volume-root / --update-all --force
   ```
4. Reinicie o notebook.
5. No menu do OpenCore, dê boot pelo **`Macintosh HD`**.

---

## 🛠️ Método 2 (Alternativo): Stack Nativa da Apple (`NootedGreen` + `libxedrv v24`)

Caso você prefira utilizar a stack experimental compilada a partir do protótipo `GPUDriversIntel 16.0.32` da Apple (projeto de *JulioNectar*):

1. Abra o Terminal e extraia o pacote offline na sua pasta pessoal:
   ```zsh
   mkdir -p ~/xe
   tar -xzf /Volumes/HACKINTOSH/irisxe-tahoe-bundle.tar.gz -C ~/xe
   cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe
   ```
2. Instale as ferramentas de linha de comando:
   ```zsh
   xcode-select --install
   ```
3. Execute o instalador automatizado:
   ```zsh
   zsh install.sh
   ```
4. Ative a configuração correspondente no pendrive:
   ```zsh
   cp /Volumes/HACKINTOSH/EFI/OC/config-nootedgreen.plist /Volumes/HACKINTOSH/EFI/OC/config.plist
   sync
   ```
5. Permita as extensões em **Ajustes do Sistema > Privacidade e Segurança** e reinicie.

---

## ✅ Como Confirmar que a Aceleração Metal Está 100% Ativa

Ao iniciar o macOS após a aplicação de um dos métodos, você notará imediatamente a diferença visual:
* O Dock e a Barra de Menus estarão translúcidos com efeito de vidro (*blur/Liquid Glass*).
* As animações de janelas, Mission Control e Launchpad rodarão a 60 FPS com suavidade absoluta.

Para verificar via linha de comando no Terminal:
```zsh
system_profiler SPDisplaysDataType
```

**Resultado esperado:**
* **Chipset Model:** `Intel Iris Xe Graphics`
* **Type:** `GPU`
* **Bus:** `Built-In`
* **VRAM (Total):** `1536 MB` (ou alocação dinâmica)
* **Metal Support:** `Metal 2` / `Metal 3`
