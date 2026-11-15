import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_REPO = ROOT / "deps" / "Hackintosh-XPS13Plus-IrisXe-Tahoe"
DIST = ROOT / "dist"
BUNDLE_PATH = DIST / "irisxe-tahoe-bundle.tar.gz"
GUIDE_PATH = DIST / "LEIAME-INSTALACAO.md"

INSTALL_GUIDE_MD = """# Guia Prático de Instalação: macOS Tahoe 26.7.1 no Dell Inspiron 15 5510

Este pacote (`dist/`) foi gerado e validado especificamente para o seu **Dell Inspiron 15 5510** (`Core i5-11320H` + `Intel Iris Xe 8086:9A49` 96 EU).

---

## Passo 1: Configuração da BIOS Dell (Tecla F2 ao ligar)

1. **Storage / SATA Operation:** Mantenha em **AHCI/NVMe** (já confirmado ativo no seu notebook — **não** mude para RAID).
2. **Secure Boot:** Mude para **Disabled (Desativado)**.
3. **VT-d / Virtualization:** Pode manter **Enabled**.
4. Salve e reinicie.

---

## Passo 2: Instalação do macOS Tahoe 26.7.1 (build `25G241`)

1. No pendrive preparado pelo script `prepare_dualboot.ps1`, a pasta `EFI/OC/config.plist` já inicia no **modo seguro de instalação (VESA)** (`config-install.plist`), e a versão acelerada fica salva ao lado como `EFI/OC/config-accelerated.plist`.
2. Dê boot pelo pendrive (**Tecla F12** ao ligar -> selecione a partição UEFI do pendrive).
3. No menu do **OpenCore**, escolha o instalador do **macOS Tahoe**.
4. Abra o **Utilitário de Disco (Disk Utility)**:
   - Clique em **Visualizar (View) > Mostrar Todos os Dispositivos (Show All Devices)**.
   - Selecione a partição de **128 GB** criada para o macOS (nunca apague a partição `C:` do Windows!) e clique em **Apagar (Erase)**:
     - **Nome:** `Macintosh HD`
     - **Formato:** `APFS`
   - Feche o Utilitário de Disco e instale o **macOS Tahoe 26.7.1 (25G241)** em `Macintosh HD`.
   - O notebook reiniciará de 2 a 3 vezes; sempre dê boot pelo pendrive e selecione `macOS Installer` / `Macintosh HD`.

---

## Passo 3: Ativando a Aceleração Metal 2 da Intel Iris Xe (`8086:9A49`)

Assim que chegar à área de trabalho do macOS Tahoe 26.7.1 (ainda sem aceleração gráfica, com Wi-Fi nativo funcionando):

1. Copie o arquivo `irisxe-tahoe-bundle.tar.gz` do pendrive para a sua pasta pessoal (`~`) no disco APFS e extraia-o pelo Terminal (**nunca** rode a compilação direto do pendrive FAT32!):
   ```zsh
   mkdir -p ~/xe
   tar -xzf /Volumes/*/irisxe-tahoe-bundle.tar.gz -C ~/xe
   cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe
   ```
2. Instale o Command Line Tools da Apple (apenas uma vez):
   ```zsh
   xcode-select --install
   ```
3. Execute o instalador automatizado do stack Iris Xe (ele baixa os bundles `16.0.32` do NootedGreen, compila `NootedGreen.kext`, `HookCase.kext`, `libxedrv` e instala os drivers em `/Library/Extensions` e `/Library/GPUBundles`):
   ```zsh
   zsh install.sh
   ```
4. Copie a `NootedGreen.kext` recém-compilada e ative o `config.plist` acelerado na EFI do pendrive:
   ```zsh
   # Substitua /Volumes/USB pela partição EFI do pendrive:
   cp -R build/NootedGreen.kext /Volumes/USB/EFI/OC/Kexts/
   cp /Volumes/USB/EFI/OC/config-accelerated.plist /Volumes/USB/EFI/OC/config.plist
   ```
5. Se o macOS abrir um aviso em **Ajustes do Sistema > Privacidade e Segurança**, clique em **Permitir (Allow)** para as extensões de kernel e **reinicie**.

---

## Passo 4: Ajustes Pós-Boot Acelerado (Resolução, Brilho, Tampa e Decodificação de Vídeo)

Após reiniciar com a aceleração Metal 2 ativa (confira em `system_profiler SPDisplaysDataType | grep Metal`):

```zsh
cd ~/xe/Hackintosh-XPS13Plus-IrisXe-Tahoe

# 1. Evitar que o fechamento da tampa trave em S3 Sleep (apaga apenas a tela):
sudo zsh tools/sleep/10-pmset-safe.sh
zsh tools/sleep/install-xe-lid.sh

# 2. Compilar controle de resolução/HiDPI (xe-res) e brilho (xe-brilho):
mkdir -p tools/build
clang -O2 -o tools/build/xe-res tools/xe-res.c -framework CoreGraphics -framework CoreFoundation
clang -O2 -fobjc-arc -DXECTL_NO_MAIN -o tools/build/xe-brilho tools/xe-brilho.m tools/xectl.c -framework AppKit -framework IOKit

# 3. Monitor de temperatura e potência na barra de menus (xe-temp):
zsh tools/xe-temp/build.sh && cp -R tools/build/xe-temp.app ~/Applications/
open ~/Applications/xe-temp.app
```

> **Dica de Segurança:** Mantenha sempre um pendrive com `config-install.plist` guardado. Caso precise testar outros layouts de áudio interno do Realtek ALC236, basta trocar `alcid=11` nos `boot-args` por `alcid=3`, `alcid=13`, `alcid=15`, `alcid=54` ou `alcid=99` (o seu dispositivo de áudio USB funciona nativamente sem configuração adicional).
"""


def reset_tarinfo_perms(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
    if tarinfo.name.endswith((".sh", ".py")) or "/MacOS/" in tarinfo.name:
        tarinfo.mode = 0o755
    return tarinfo


def pack_bundle() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    with tarfile.open(BUNDLE_PATH, "w:gz") as tf:
        tf.add(
            BASE_REPO,
            arcname="Hackintosh-XPS13Plus-IrisXe-Tahoe",
            filter=reset_tarinfo_perms,
        )
    GUIDE_PATH.write_text(INSTALL_GUIDE_MD, encoding="utf-8")


if __name__ == "__main__":
    pack_bundle()
    print(f"Bundle created at {BUNDLE_PATH} ({BUNDLE_PATH.stat().st_size} bytes).")
