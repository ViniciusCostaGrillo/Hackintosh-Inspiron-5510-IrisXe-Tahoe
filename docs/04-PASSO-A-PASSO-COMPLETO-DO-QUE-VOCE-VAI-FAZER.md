# 04 — Passo a Passo Completo do Que Você Vai Precisar Fazer Agora

> **STATUS ATUAL:**
> ✅ **O instalador do macOS Tahoe 26.7.1 (`25G241`) deu boot com sucesso no seu Dell Inspiron 15 5510!**
> O congelamento em `shared_region ... [1(launchd)] check` / `libignition` foi 100% superado após aplicarmos o spoof limpo de Comet Lake para CPUs Tiger Lake de 4 núcleos e corrigirmos o driver NVMe da ADATA.

---

## 📊 Resumo do Sucesso e Estado Atual da Máquina

1. **No seu SSD Interno (`Disk 0`):**
   * **Partição `C:` (Windows 11):** `~122 GB` — Intacta e funcionando normalmente.
   * **Partição `MACOS`:** `~115 GB` (formatada temporariamente em `exFAT` com o nome **`MACOS`**) — Pronta para você selecionar no Utilitário de Disco do macOS e formatar como **APFS (`Macintosh HD`)**.
2. **No seu Pendrive `HACKINTOSH (D:)`:**
   * **`D:\EFI\OC\config.plist`:** Configuração validada com sucesso, rodando em modo de instalação seguro:
     * CPUID Spoof limpo de Comet Lake (`55060A00 00000000 00000000 00000000` / `FFFFFFFF 00000000 00000000 00000000`).
     * `NVMeFix.kext` ativa + `SetApfsTrimTimeout = -1` (estabiliza o SSD ADATA SM2P41C3).
     * `WhateverGreen.kext` com a flag `-igfxvesa` (ambiente gráfico estável para a instalação).
     * `itlwm.kext` ativada com pré-configuração para rede Wi-Fi.
   * **`D:\WhateverXe-Graphics-0.4.4.pkg` (`90,8 MB`):** Pacote de instalação 1-clique dos drivers gráficos da Intel Iris Xe Metal pós-instalação!
   * **`D:\EFI\OC\config-whateverxe.plist`:** Configuração pós-instalação para aceleração gráfica com WhateverXe.
   * **`D:\EFI\OC\config-nootedgreen.plist`:** Configuração alternativa com a stack NootedGreen + driver protótipo da Apple.

---

## 🌐 Etapa 1: Conectar à Internet na Recuperação do macOS

Para baixar os arquivos de instalação do macOS Tahoe pela Apple, você precisa de internet ativa:

### Opção A (Mais Rápida e Prática): Ancoragem USB via Celular (Samsung Galaxy A55)
1. Conecte o cabo USB do seu celular Samsung Galaxy A55 no notebook.
2. No celular, vá em **Configurações > Conexões > Roteador Wi-Fi e Ancoragem > Ancoragem via USB (USB Tethering)** e ative.
3. O instalador do macOS reconhece a conexão imediatamente como rede cabeada (Ethernet), sem necessidade de senha!

### Opção B: Wi-Fi com `itlwm.kext`
* A `itlwm.kext` já está carregada no seu pendrive. Ela emula uma placa de rede Ethernet (`en0`).
* Se a sua rede estiver pré-configurada no `Info.plist`, a conexão subirá automaticamente em segundo plano.

---

## 💽 Etapa 2: Formatar a Partição no Utilitário de Disco

1. Na tela principal de Recuperação do macOS, clique em **Utilitário de Disco (Disk Utility)** e em **Continuar**.
2. No menu superior esquerdo, clique em **Visualizar (View)** → **Mostrar Todos os Dispositivos (Show All Devices)**.
3. Na barra lateral esquerda, localize a partição chamada **`MACOS`** (de **~115 GB** a **123 GB** no SSD ADATA).
   * ⚠️ **ATENÇÃO:** Selecione **apenas** a partição `MACOS`! Nunca apague ou formate a partição do Windows (`BOOTCAMP` / `C:`).
4. Clique no botão **Apagar (Erase)** na barra de ferramentas superior:
   * **Nome:** `Macintosh HD`
   * **Formato:** `APFS`
   * **Esquema:** (se solicitado) Deixe como está (a tabela já é GUID Partition Map).
5. Clique em **Apagar (Erase)**. Aguarde alguns segundos até concluir e clique em **OK**.
6. Feche o Utilitário de Disco (`Command + Q` ou botão vermelho superior esquerdo).

---

## 🚀 Etapa 3: Instalar o macOS Tahoe

1. Na tela inicial de Recuperação, clique em **Reinstalar o macOS (Reinstall macOS)** → **Continuar**.
2. Concorde com os termos de licença da Apple.
3. Na seleção de disco de destino, selecione o disco **`Macintosh HD`** que você acabou de criar.
4. Clique em **Instalar**.
5. O instalador iniciará o download e cópia dos arquivos do sistema. Esse processo leva cerca de 25 a 45 minutos dependendo da sua velocidade de internet.
6. **Reinicializações automáticas:**
   * O computador irá reiniciar **2 a 3 vezes** durante o processo.
   * **Em cada reinicialização:** Pressione a tecla **F12** da Dell, selecione o **Pendrive UEFI**, e no menu do OpenCore selecione:
     * 1ª e 2ª reinicializações: **`macOS Installer`**
     * Na última reinicialização: **`Macintosh HD`**
7. Conclua a tela de boas-vindas do macOS (configuração de idioma, teclado, conta de usuário e senha).
8. Você chegará com sucesso na **Área de Trabalho do macOS Tahoe** (em modo de vídeo seguro VESA)!

---

## ⚡ Etapa 4: Ativar a Aceleração Metal da Intel Iris Xe (Pós-Instalação)

Agora que você já está na Área de Trabalho com acesso completo ao disco:
* Abra o manual:
  👉 **[05 — Passo a Passo Exclusivo: Ativação da Placa Gráfica Intel Iris Xe](./05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md)**

Você usará o pacote **`WhateverXe-Graphics-0.4.4.pkg`** que já está salvo no pendrive para ativar a aceleração em apenas 1 clique!
