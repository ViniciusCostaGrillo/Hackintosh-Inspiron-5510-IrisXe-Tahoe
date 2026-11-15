# 05 — Passo a Passo Exclusivo: Ativação da Placa Gráfica Intel Iris Xe (`8086:9A49` — Metal 2)

> **Equipamento:** Dell Inspiron 15 5510 — Intel Core i5-11320H (`Family 6 Model 140 / 0x8C`, Tiger Lake-UP3/H35)
> **GPU:** Intel Iris Xe Graphics (`PCI\VEN_8086&DEV_9A49`, 96 Execution Units, 8 bancos L3, Display Engine 12)
> **Sistema Alvo Exigido:** macOS Tahoe **26.7.1** (Build exata **`25G241`**)
> **Arquitetura do Driver:** Apple Prototype `GPUDriversIntel 16.0.32` + `NootedGreen.kext` + `HookCase.kext` + `libxedrv.dylib` (v24) + Ponte de Shaders `LLVM 3902 → 32023`

---

## 🧠 Como Funciona a Ativação em 2 Fases (Resumo Rápido)

1. **Fase 1 — Instalação Segura (Modo VESA — Já configurado no seu Pendrive `D:`):**
   * O arquivo `D:\EFI\OC\config.plist` atual usa a flag `-igfxvesa` e está com a `NootedGreen.kext` **desativada**.
   * Isso é obrigatório porque os drivers gráficos da Iris Xe precisam ser instalados dentro da partição `/Library/Extensions` e `/Library/GPUBundles` do macOS. Se a `NootedGreen.kext` estivesse ativa antes de você instalar o macOS, o instalador travaria procurando arquivos que ainda não existem no SSD.
2. **Fase 2 — Ativação da Aceleração Total Metal 2 (Pós-Instalação):**
   * Assim que você terminar de instalar o macOS Tahoe 26.7.1 (`25G241`) no disco `Macintosh HD` e entrar na Área de Trabalho pela primeira vez, você rodará os passos abaixo para instalar os bundles gráficos, ativar a `NootedGreen.kext` e trocar o `config.plist` pelo `config-accelerated.plist`.

---

## 🚀 Passo a Passo Completo para Ativar a Intel Iris Xe no macOS

Execute todos os passos abaixo **dentro do macOS Tahoe 26.7.1 (`25G241`)**, logo após concluir a instalação e chegar na Área de Trabalho (com o pendrive `HACKINTOSH` plugado no notebook).

### Passo 1: Confirmar a Build do macOS no Terminal
Abra o aplicativo **Terminal** (`Command + Espaço` → digite `Terminal`) e verifique se a versão instalada é a `25G241`:

```zsh
sw_vers
```
> **Importante:** O campo `BuildVersion` deve ser **`25G241`** (macOS 26.7.1). Os patches binários do `NootedGreen` e do `patch-mtl17.py` foram calibrados especificamente para essa build.

---

### Passo 2: Extrair o Pacote da Iris Xe na sua Partição APFS (`~/xe`)
No seu pendrive `HACKINTOSH`, já deixamos pronto o arquivo compactado **`irisxe-tahoe-bundle.tar.gz`** (`81,8 MB`).

> ⚠️ **REGRA DE OURO:** **NUNCA** extraia nem rode a compilação dentro do pendrive (`FAT32`), pois sistemas FAT32 criam arquivos ocultos `._` (AppleDouble) que corrompem a assinatura digital (`codesign`) dos binários `.kext` e `.bundle` no macOS! Sempre extraia na sua pasta pessoal (`~/xe`) dentro do SSD APFS.

No Terminal, execute:

```zsh
mkdir -p ~/xe
tar -xzf /Volumes/HACKINTOSH/irisxe-tahoe-bundle.tar.gz -C ~/xe
cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe
```

*(Caso o macOS tenha montado o pendrive com outro nome em `/Volumes/`, você pode usar o curinga `tar -xzf /Volumes/*/irisxe-tahoe-bundle.tar.gz -C ~/xe`).*

---

### Passo 3: Instalar o Command Line Tools da Apple
O script de ativação precisa do compilador `clang`, `codesign` e `python3` da Apple para compilar a `libxedrv.dylib` (v24) e assinar localmente os bundles da GPU.

No Terminal, execute:

```zsh
xcode-select --install
```
* Uma janela do macOS aparecerá pedindo confirmação para instalar as ferramentas de linha de comando.
* Clique em **Instalar (Install)** e **aguarde terminar 100%** antes de prosseguir para o Passo 4.

---

### Passo 4: Executar o Instalador Automatizado do Driver (`install.sh`)
Ainda dentro da pasta `~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe`, execute:

```zsh
zsh install.sh
```

#### O que o `install.sh` faz automaticamente para você:
1. **Valida o ambiente:** Confirma a build `25G241` e as ferramentas do Xcode.
2. **Obtém os binários `16.0.32` da Apple:** Extrai os 7 bundles originais da Intel Tiger Lake (`AppleIntelTGLGraphics.kext`, `AppleIntelTGLGraphicsFramebuffer.kext`, `AppleIntelTGLGraphicsMTLDriver.bundle`, `AppleIntelTGLGraphicsVADriver.bundle`, `AppleIntelTGLGraphicsVAME.bundle`, `IntelMetrics.bundle`, `AppleIntelICLLPGraphicsVAME.bundle`).
3. **Compila as Kexts de Kernel:** Compila a `NootedGreen.kext` e a `HookCase.kext` em `build/`.
4. **Aplica os Patches de User-Space Metal 2 (`macos/install-macos.sh`):**
   * Roda `patch-mtl17.py` no `AppleIntelTGLGraphicsMTLDriver.bundle` (17 patches binários para compatibilizar a API do Metal 2 do macOS Tahoe com o driver de 2020).
   * Compila e injeta a biblioteca `libxedrv.dylib` (**v24**) — que gerencia a submissão de comandos para os **96 Execution Units** e os **8 bancos de cache L3** da sua `8086:9A49`.
   * Compila e instala a ponte de shaders (`compiler-adapter` + `llvm-bridge`) que traduz o bytecode Air/Bitcode do `LLVM 32023` (Tahoe) para `LLVM 3902` (driver Intel).
5. **Instala nas Pastas do Sistema e Reconstrói o Cache:**
   * Copia as kexts para `/Library/Extensions/` e os bundles para `/Library/GPUBundles/`.
   * Executa `sudo kmutil install --volume-root / --update-all --force`.

---

### Passo 5: Autorizar as Extensões de Kernel nos Ajustes do Sistema
Durante o `install.sh` (quando o `kmutil` rodar), o macOS exibirá um aviso de **Extensão do Sistema Bloqueada (System Extension Blocked)**:
1. Abra **Ajustes do Sistema (System Settings) > Privacidade e Segurança (Privacy & Security)**.
2. Role até o fim da página e clique em **Permitir (Allow)** ao lado das extensões recém-instaladas.
3. Digite sua senha do macOS.
4. Se o `install.sh` tiver pedido para rodar novamente após autorizar, ou para garantir que o cache foi reconstruído, rode no Terminal:
   ```zsh
   sudo kmutil install --volume-root / --update-all --force
   ```
   *(Não reinicie ainda! Antes de reiniciar, faça o Passo 6 abaixo).*

---

### Passo 6: Copiar a `NootedGreen.kext` e Ativar o `config-accelerated.plist` no Pendrive
Agora que os drivers já estão instalados no macOS, precisamos ativar o modo acelerado no OpenCore do pendrive `HACKINTOSH`:

No Terminal, execute:

```zsh
# 1. Atualiza a NootedGreen.kext recém-compilada na EFI do pendrive:
cp -R ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe/build/NootedGreen.kext /Volumes/HACKINTOSH/EFI/OC/Kexts/

# 2. Substitui o config.plist de instalação (VESA) pelo config-accelerated.plist (Metal 2):
cp /Volumes/HACKINTOSH/EFI/OC/config-accelerated.plist /Volumes/HACKINTOSH/EFI/OC/config.plist

# 3. Garante que tudo foi gravado no pendrive:
sync
```

#### O que muda no `config-accelerated.plist` (já configurado sob medida para o seu Inspiron 5510):
* **Ativa a `NootedGreen.kext`** (`Enabled = true`) no carregamento do kernel.
* **Injeta as propriedades PCI da sua Iris Xe em `PciRoot(0x0)/Pci(0x2,0x0)`:**
  * `AAPL,ig-platform-id`: `<0000499A>`
  * `device-id`: `<499A0000>`
  * `model`: `"Intel Iris Xe Graphics"`
* **Substitui `-igfxvesa` pelas flags completas de aceleração Tiger Lake nos `boot-args`:**
  ```text
  -v keepsyms=1 debug=0x100 IGLogLevel=3 -ngreentglwithgfx -allow3d -disablegfxfirmware ngreen-dmc=tgl -ngreenv189 -ngreenkeepefi -ngreenxefix -ngreenfixbootmode amfi_get_out_of_my_way=1 ngreenSched=4 ngreenV142=3 gfxrst=1 ngreenpm=22 alcid=11
  ```
  * `ngreen-dmc=tgl`: Carrega o firmware nativo Tiger Lake DMC v2.12 e ativa a proteção `V101T`/`V102T`/`V103` das Power Wells para nunca perder interrupção de VSync.
  * `-ngreenv189`: Ativa o patch inteligente de sinalização `AccessComplete` no DYLD, evitando travamentos de 234 ms do `WindowServer`.
  * `-ngreenkeepefi -ngreenfixbootmode`: Corrige o modo inicial `0xfffffffb` (`kIOFBBootProgrammable`) lendo os timings reais 1920x1080 do CRTC da sua tela.
  * `ngreenV142=3`: Habilita o motor nativo de Blit 3D do silício Tiger Lake real.
  * `ngreenpm=22`: Ativa o gerenciamento de energia HWP (`PL1 = 22W`) e tabela de estados ociosos C-state.
* **Limpa a NVRAM (`Delete > boot-args`):** Força o OpenCore a descartar o `-igfxvesa` antigo salvo na NVRAM e aplicar imediatamente as flags do Metal 2.

Agora **reinicie o notebook** e dê boot novamente pelo pendrive (`F12`).

---

## ✅ Passo 7: Verificar se a Aceleração Metal 2 Está Ativa

Assim que o macOS iniciar após o reboot, você já notará a diferença visual imediatamente: **a barra do Dock ficará translúcida (efeito Liquid Glass), as animações rodarão a 60 Hz suaves e o ícone "Sobre Este Mac" mostrará `Intel Iris Xe Graphics 1536 MB`**.

Para confirmar via Terminal, execute:

```zsh
# 1. Verifica se a NootedGreen e os drivers TGL estão carregados no kernel:
kmutil showloaded | grep -E "NootedGreen|TGL"

# 2. Verifica o suporte a Metal e a VRAM reconhecida:
system_profiler SPDisplaysDataType
```
Você deverá ver:
* `Chipset Model: Intel Iris Xe Graphics`
* `VRAM (Dynamic, Max): 1536 MB`
* `Metal Support: Metal 2`

---

## 🛠️ Passo 8: Instalar as Ferramentas Complementares da Iris Xe (Resolução, Brilho, Tampa e Temperatura)

Com a aceleração ativa, rode estes comandos no Terminal para compilar e ativar os utilitários da Iris Xe:

```zsh
cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe

# 1. Configurar fechamento seguro da tampa (apaga a tela sem travar em S3 Sleep):
sudo zsh tools/sleep/10-pmset-safe.sh
zsh tools/sleep/install-xe-lid.sh

# 2. Compilar os utilitários de Resolução HiDPI (xe-res) e Brilho (xe-brilho):
mkdir -p tools/build
clang -O2 -o tools/build/xe-res tools/xe-res.c -framework CoreGraphics -framework CoreFoundation
clang -O2 -fobjc-arc -DXECTL_NO_MAIN -o tools/build/xe-brilho tools/xe-brilho.m tools/xectl.c -framework AppKit -framework IOKit
sudo cp tools/build/xe-res tools/build/xe-brilho /usr/local/bin/

# 3. Compilar e abrir o monitor de temperatura e consumo em Watts na barra de menus (xe-temp):
zsh tools/xe-temp/build.sh
mkdir -p ~/Applications
cp -R tools/build/xe-temp.app ~/Applications/
open ~/Applications/xe-temp.app
```

### Como usar os utilitários no dia a dia:
* **Trocar resolução / escala HiDPI (`xe-res`):**
  > ⚠️ **Dica:** Sempre use o `xe-res` pelo Terminal em vez do painel "Telas" dos Ajustes do Sistema para evitar piscadas do `WindowServer`.
  ```zsh
  xe-res list          # Lista todas as resoluções disponíveis
  xe-res 1920 1080     # Define 1080p nativo
  xe-res 1600 900      # Define escala mais confortável com elementos maiores
  ```
* **Ajustar o brilho da tela (`xe-brilho`):**
  ```zsh
  xe-brilho            # Abre o controle deslizante flutuante de brilho na tela
  xe-brilho 75         # Define o brilho diretamente em 75%
  ```

---

## 🛟 Plano de Contingência (Como Reverter para Modo VESA se Algo Der Errado)

Se por qualquer motivo você quiser voltar ao modo seguro sem aceleração (por exemplo, se esquecer de autorizar uma kext antes de trocar o `config.plist`):

1. **Pelo Windows (ou qualquer PC):**
   * Abra o pendrive `HACKINTOSH (D:)`.
   * Na pasta `D:\EFI\OC\`, copie o arquivo `config-install.plist` por cima do `config.plist`:
     ```powershell
     Copy-Item "D:\EFI\OC\config-install.plist" "D:\EFI\OC\config.plist" -Force
     ```
2. **Para desinstalar os drivers no macOS e recomeçar limpo:**
   ```zsh
   cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe
   zsh install.sh --uninstall
   ```
