# 04 — Passo a Passo Completo do Que Você Vai Precisar Fazer Agora

> **STATUS ATUAL (15/11/2026):**
> ✅ **A Etapa 1 (Preparar o Dual-Boot no SSD e montar o Pendrive `HACKINTOSH D:`) JÁ FOI 100% EXECUTADA AUTOMATICAMENTE!**
> Você **não** precisa mais rodar nenhum comando no Windows. Seu notebook já está pronto para reiniciar e dar boot no instalador!

---

## 📊 Resumo do Que Já Está Pronto no Seu Computador e no Pendrive `D:`

1. **No seu SSD Interno (`Disk 0`):**
   * **Partição `C:` (Windows 11):** `131,44 GB` (`122,41 GiB`) — Intacta e funcionando normalmente.
   * **Partição `E:` (`MACOS`):** `123,48 GB` (`115 GiB`, formatada em `exFAT` com o nome **`MACOS`**) — Pronta para você selecionar no Utilitário de Disco do macOS e formatar como `APFS` (`Macintosh HD`).
2. **No seu Pendrive `HACKINTOSH (D:)`:**
   * **`D:\EFI\`:** OpenCore 1.0.8 sob medida para o seu Dell Inspiron 15 5510 (`SSDT-I2C1.aml`, `UTBMap.kext`, `AirportItlwm.kext`, `AppleALC.kext`), com o modo seguro (`config-install.plist`) já ativo como `D:\EFI\OC\config.plist` e o modo acelerado salvo em `D:\EFI\OC\config-accelerated.plist`.
   * **`D:\com.apple.recovery.boot\`:** Imagem oficial da Apple (`BaseSystem.dmg` de `960,5 MB` + `BaseSystem.chunklist`) baixada e verificada.
   * **`D:\irisxe-tahoe-bundle.tar.gz` (`81,8 MB`):** Pacote completo com os drivers Metal 2 da Intel Iris Xe (`8086:9A49`), `NootedGreen`, `libxedrv v24` e `install.sh`.
   * **`D:\05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md`:** Cópia do manual da Iris Xe dentro do próprio pendrive para você abrir direto no macOS!

---

## 🔧 Etapa 1 (Agora): Configurar a BIOS do Dell Inspiron 15 5510

1. Com o pendrive `HACKINTOSH (D:)` espetado no notebook, clique em **Reiniciar** no Windows.
2. Assim que a tela apagar e o logo da Dell aparecer, pressione a tecla **F2** repetidamente para entrar na BIOS.
3. No menu da BIOS da Dell, confira estas **2 opções obrigatórias**:
   * **Boot Configuration > Secure Boot:** Mude para **`Disabled` (Desativado)**.
   * **Storage > SATA/NVMe Operation:** Confirme que está em **`AHCI/NVMe`** *(ele já está nesse modo; **nunca** mude para RAID On)*.
4. Clique no botão **Apply Changes** na parte inferior e depois em **Exit**.

---

## 💿 Etapa 2: Dar Boot pelo Pendrive e Instalar o macOS

1. Assim que o notebook reiniciar após sair da BIOS, pressione a tecla **F12** repetidamente para abrir o **One-Time Boot Menu** da Dell.
2. Em **UEFI Boot Devices**, selecione o seu **Pendrive USB (`UEFI: ... Partition 1`)** e pressione **Enter**.
3. O menu do **OpenCore** aparecerá na tela:
   * Selecione a opção **`HACKINTOSH (dmg)`** ou **`macOS Base System` / `Install macOS`** (caso ela não apareça de primeira, pressione a **Barra de Espaço** no teclado dentro do menu do OpenCore para revelar as opções auxiliares e selecione o dmg de Recovery).
   * Pressione **Enter**. Você verá várias linhas de texto brancas passando na tela (modo *verbose* `-v`) e, em seguida, entrará na tela de **Recuperação do macOS**.
4. **Conectar ao Wi-Fi (se estiver instalando via Recovery Online):**
   * Olhe no canto superior direito da tela (ícone de Wi-Fi) ou na janela central e conecte-se à sua rede Wi-Fi (ou use cabo de rede/ancoragem USB do celular).
5. **Formatar a Partição `MACOS` como APFS no Utilitário de Disco:**
   * Na janela principal, clique em **Utilitário de Disco (Disk Utility)** e em **Continuar**.
   * Na barra lateral esquerda, procure a partição chamada **`MACOS`** (de **~123,5 GB**).
   * ⚠️ **ATENÇÃO:** Selecione **apenas** a partição **`MACOS`**! Não apague a partição do Windows.
   * Clique no botão **Apagar (Erase)** no topo da janela e preencha:
     * **Nome:** `Macintosh HD`
     * **Formato:** `APFS`
   * Clique em **Apagar**, aguarde concluir e feche a janela do Utilitário de Disco (`Command + Q` ou botão vermelho no canto superior esquerdo).
6. **Iniciar a Instalação do macOS:**
   * Na tela principal, clique em **Reinstalar o macOS (Reinstall macOS)** → **Continuar**.
   * Aceite os termos e selecione o disco **`Macintosh HD`** que você acabou de criar.
   * O notebook fará o download/cópia dos arquivos e **reiniciará sozinho de 2 a 3 vezes**.
   * **Em cada reinicialização:** Pressione **F12**, selecione o **Pendrive UEFI**, e no menu do OpenCore selecione **`macOS Installer`** (nas primeiras vezes) e depois **`Macintosh HD`** (quando o nome mudar para `Macintosh HD`).

> ⚠️ **IMPORTANTE SOBRE A VERSÃO DO MACOS TAHOE 26.7.1 (`25G241`):**
> * Os drivers de aceleração Metal 2 da Intel Iris Xe exigem o **macOS Tahoe 26.7.1 (build `25G241`)**.
> * Se a Recuperação Online da Apple instalar primeiro uma versão anterior do macOS (como Sonoma/Sequoia) no seu `Macintosh HD`, basta concluir a criação do seu usuário no macOS e, de dentro dele, atualizar/instalar o instalador completo do **macOS Tahoe 26.7.1 (`25G241`)** mantendo o `config-install.plist` (modo VESA) ativo até estar na build `25G241`.

---

## ⚡ Etapa 3: Ativar a Aceleração Metal 2 da Intel Iris Xe (`8086:9A49`)

Assim que você estiver na Área de Trabalho do **macOS Tahoe 26.7.1 (`25G241`)**, abra o arquivo dedicado:
👉 **[05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md](./05-PASSO-A-PASSO-EXCLUSIVO-ATIVACAO-IRIS-XE.md)** *(que também está salvo na raiz do seu pendrive `HACKINTOSH`!)*

Lá estão os comandos exatos para copiar e colar no Terminal do macOS:
1. Extrair o `irisxe-tahoe-bundle.tar.gz` em `~/xe`
2. Rodar `xcode-select --install`
3. Rodar `zsh install.sh`
4. Autorizar as extensões em **Ajustes do Sistema > Privacidade e Segurança**
5. Copiar a `NootedGreen.kext` e ativar o `config-accelerated.plist` como `config.plist` no pendrive.

---

## 🔄 Etapa 4 (Opcional): Tornar o Dual-Boot Independente do Pendrive

Depois que tudo estiver funcionando com aceleração Metal 2 e você não quiser mais precisar do pendrive plugado para ligar o notebook:

1. No Terminal do macOS, monte a partição EFI do SSD interno (`disk0s1`):
   ```zsh
   sudo diskutil mount disk0s1
   ```
2. Copie as pastas `OC` e `BOOT` do pendrive para dentro da partição EFI do SSD (**sem apagar** a pasta `Microsoft` que já existe lá!):
   ```zsh
   cp -R /Volumes/HACKINTOSH/EFI/OC /Volumes/EFI/EFI/
   cp -R /Volumes/HACKINTOSH/EFI/BOOT /Volumes/EFI/EFI/
   ```
3. Reinicie o notebook, entre na BIOS (**F2 > Boot Configuration**), clique em **Add Boot Option**, escolha o arquivo `\EFI\OC\OpenCore.efi` no SSD NVMe, dê o nome `OpenCore` e mova-o para o topo da ordem de boot.
4. Pronto! Sempre que ligar o notebook, o menu do OpenCore perguntará se você quer entrar no **macOS Tahoe** ou no **Windows 11**.
