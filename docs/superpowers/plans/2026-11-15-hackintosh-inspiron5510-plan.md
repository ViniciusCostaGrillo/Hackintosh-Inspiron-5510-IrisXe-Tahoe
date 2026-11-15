# Dell Inspiron 15 5510 Hackintosh (macOS Tahoe 26.7.1 + Iris Xe Metal) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir a EFI OpenCore 1.0.8 sob medida para o Dell Inspiron 15 5510 (Core i5-11320H + Intel Iris Xe `8086:9A49` 96 EU), empacotar o stack de aceleração Metal (`NootedGreen` + `libxedrv v24`) e preparar o ambiente de Dual-Boot e mídia de instalação do macOS Tahoe 26.7.1 (`25G241`) a partir do Windows.

**Architecture:** Um pipeline automatizado em Python e PowerShell rodando no Windows extrai e compila as tabelas ACPI reais da máquina (`acpidump`/`iasl`), gera o mapeamento USB (`UTBMap.kext`), constrói e valida a árvore `dist/EFI` com `ocvalidate.exe` (em duas variantes: `config-install.plist` em modo VESA seguro e `config.plist` com aceleração Metal 2), e empacota o código-fonte do `Hackintosh-XPS13Plus-IrisXe-Tahoe` + `NootedGreen` (`95f8189`) em `.tar.gz` para execução pós-instalação no volume APFS.

**Tech Stack:** OpenCore 1.0.8 (`ocvalidate`, `macserial`), ACPICA (`acpidump.exe`, `iasl.exe`), Python 3.11+ (`plistlib`, `pytest`), PowerShell 5.1+, `NootedGreen` (fork `JulioNectar` commit `24450b4`), `Lilu 1.7.3`, `VoodooI2C` (`VoodooGPIOTigerLakeLP`), `AirportItlwm` (Tahoe), `AppleALC`.

**Spec:** `C:\Users\Vinic\.gemini\antigravity\scratch\hackintosh-inspiron5510\docs\2026-11-09-hackintosh-inspiron5510-design.md`

## Global Constraints

- **Versão exata do macOS:** macOS Tahoe **26.7.1 (build `25G241`)** — os patches binários do `NootedGreen` e `libxedrv` exigem exatamente esta build.
- **GPU Alvo:** Intel Iris Xe `8086:9A49` (Tiger Lake GT2, 96 EU, 8 L3 banks, CPU Family 6 Model 140 / `0x8C`) em `\_SB.PC00.GFX0` (`PciRoot(0x0)/Pci(0x2,0x0)`).
- **SMBIOS:** `MacBookPro16,2` com números de série (`SystemSerialNumber`, `MLB`, `SystemUUID`, `ROM`) gerados localmente via `macserial.exe` e nunca compartilhados.
- **Preservação do Windows:** A partição `C:` deve manter no mínimo 120 GB totais (~60 GB livres além dos 65 GB em uso); nenhuma operação de disco pode tocar nas partições 1 (EFI), 2 (MSR) ou 4 (Recovery).
- **Proteção contra corrupção FAT32 (`._` AppleDouble):** Os bundles `16.0.32` do `NootedGreen` e o repositório `Hackintosh-XPS13Plus-IrisXe-Tahoe` devem ser transportados para o macOS dentro de um arquivo `.tar.gz` e extraídos somente dentro do disco APFS (`~/xe`).

## Review Focus

1. **`NVRAM > Delete > boot-args` omitido:** Se `boot-args` não estiver listado em `NVRAM > Delete > 7C436110-AB2A-4BBB-A880-FE41995C9F82`, o OpenCore ignora mudanças de `boot-args` ao alternar entre `config-install.plist` e `config.plist`. O teste de configuração deve exigir `boot-args` em `Add` e `Delete`.
2. **Kexts/SSDTs exclusivos do XPS 13 Plus (Raptor Lake) esquecidos na EFI:** `CpuTopologyRebuild.kext` (trava CPUs não-híbridas sem E-cores), `SSDT-XPS-I2C.aml` (aponta para `TPL0` inexistente) e `UTBDefault.kext` (mapa USB do XPS) devem estar ausentes ou desativados na EFI final.
3. **Falta do `HfsPlus.efi`:** O repositório base não inclui `HfsPlus.efi` por licença; sem ele o OpenCore não enxerga imagens de instalação HFS+/DMG. O teste deve verificar a presença física de `EFI/OC/Drivers/HfsPlus.efi` e sua entrada em `UEFI > Drivers`.
4. **Conflito entre `config-install.plist` e `NootedGreen.kext`:** No `config-install.plist`, a entrada `NootedGreen.kext` deve estar com `Enabled = False` e `-igfxvesa` presente nos `boot-args`, garantindo que o instalador suba sem depender dos bundles em `/Library/Extensions`.
5. **Caminho ACPI do Touchpad (`DELL0B24`):** No Inspiron 15 5510, o touchpad está em `\_SB.PC00.I2C1.TPD0` (`8086:A0E9`) com controlador GPIO `\_SB.GPI0` (`INT34C5`), sem touchscreen `TPL0` em `I2C0`. A `SSDT-I2C1.aml` não pode referenciar `TPL0`.

---

## Estrutura de Arquivos do Projeto

```text
C:\Users\Vinic\.gemini\antigravity\scratch\hackintosh-inspiron5510\
├── docs\
│   ├── 2026-11-09-hackintosh-inspiron5510-design.md
│   └── superpowers\plans\2026-11-15-hackintosh-inspiron5510-plan.md
├── deps\                          # Dependências baixadas (OpenCore 1.0.8, ACPICA, AppleALC, OcBinaryData, repos)
├── acpi_dump\                     # Dump DSDT.aml / DSDT.dsl real extraído do Dell Inspiron 15 5510
├── acpi_custom\
│   └── SSDT-I2C1.dsl              # Fonte ASL para o touchpad DELL0B24 em \_SB.PC00.I2C1.TPD0
├── scripts\
│   ├── fetch_deps.py              # Baixa OpenCore 1.0.8, OcBinaryData, AppleALC, ACPICA e clona os repositórios
│   ├── build_acpi.py              # Extrai DSDT, verifica símbolos ACPI e compila SSDT-I2C1.aml
│   ├── build_usbmap.py            # Gera UTBMap.kext para os controladores 8086:A0ED (XHCI) e 8086:9A13 (TXHC)
│   ├── build_efi.py               # Monta dist/EFI, gera SMBIOS único e produz config.plist + config-install.plist
│   ├── pack_macos_bundle.py       # Empacota Hackintosh-XPS13Plus-IrisXe-Tahoe + NootedGreen 95f8189 em .tar.gz
│   └── prepare_dualboot.ps1       # Script interativo seguro para reduzir C: em 128 GB e preparar o pendrive
├── tests\
│   ├── test_acpi.py               # Testa compilação ASL e ausência de referências órfãs (TPL0)
│   ├── test_usbmap.py             # Testa UTBMap.kext (limite de 15 portas e Bluetooth interno = 255)
│   ├── test_efi_config.py         # Testa config.plist, config-install.plist e validação com ocvalidate.exe
│   └── test_bundle.py             # Testa integridade do pacote .tar.gz pós-instalação
└── dist\
    ├── EFI\                       # Pasta EFI final pronta para o pendrive (com config.plist e config-install.plist)
    ├── irisxe-tahoe-bundle.tar.gz # Pacote offline completo para rodar install.sh no macOS
    └── LEIAME-INSTALACAO.md       # Guia passo a passo (BIOS, Instalação e Pós-Instalação no macOS)
```

---

### Task 1: Aquisição de Ferramentas e Repositórios Base (`fetch_deps.py`)

**Files:**
- Create: `scripts/fetch_deps.py`
- Test: `tests/test_deps.py`

**Interfaces:**
- Produces:
  - `deps/Hackintosh-XPS13Plus-IrisXe-Tahoe/` (clone em `24450b4` ou superior)
  - `deps/OpenCore-1.0.8/Utilities/ocvalidate/ocvalidate.exe`
  - `deps/OpenCore-1.0.8/Utilities/macserial/macserial.exe`
  - `deps/OcBinaryData/Drivers/HfsPlus.efi`
  - `deps/AppleALC/AppleALC.kext`
  - `deps/acpica/acpidump.exe` e `deps/acpica/iasl.exe`

- [ ] **Step 1: Escrever o teste de verificação de dependências (`tests/test_deps.py`)**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / "deps"

def test_required_binaries_and_repos_exist():
    assert (DEPS / "Hackintosh-XPS13Plus-IrisXe-Tahoe" / "EFI" / "OC" / "config.plist").is_file()
    assert (DEPS / "OpenCore-1.0.8" / "Utilities" / "ocvalidate" / "ocvalidate.exe").is_file()
    assert (DEPS / "OpenCore-1.0.8" / "Utilities" / "macserial" / "macserial.exe").is_file()
    assert (DEPS / "OcBinaryData" / "Drivers" / "HfsPlus.efi").is_file()
    assert (DEPS / "AppleALC" / "AppleALC.kext" / "Contents" / "Info.plist").is_file()
    assert (DEPS / "acpica" / "iasl.exe").is_file()
```

- [ ] **Step 2: Rodar o teste para confirmar que falha**

Run: `pytest tests/test_deps.py -v`
Expected: FAIL (`AssertionError`)

- [ ] **Step 3: Implementar `scripts/fetch_deps.py`**

Implementar `fetch_all_deps(deps_dir: Path) -> None` em `scripts/fetch_deps.py` que:
1. Clona `https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe.git` em `deps/Hackintosh-XPS13Plus-IrisXe-Tahoe`.
2. Baixa e extrai `OpenCore-1.0.8-RELEASE.zip` de `https://github.com/acidanthera/OpenCorePkg/releases/download/1.0.8/OpenCore-1.0.8-RELEASE.zip`.
3. Baixa `HfsPlus.efi` de `https://raw.githubusercontent.com/acidanthera/OcBinaryData/master/Drivers/HfsPlus.efi`.
4. Baixa a release mais recente de `AppleALC-*-RELEASE.zip` de `acidanthera/AppleALC`.
5. Baixa o pacote oficial ACPICA Windows binaries (`iasl.exe` e `acpidump.exe`) em `deps/acpica/`.

- [ ] **Step 4: Executar `scripts/fetch_deps.py` e rodar o teste**

Run: `python scripts/fetch_deps.py && pytest tests/test_deps.py -v`
Expected: PASS

---

### Task 2: Extração ACPI Real e Compilação do `SSDT-I2C1.aml` (`build_acpi.py`)

**Files:**
- Create: `acpi_custom/SSDT-I2C1.dsl`
- Create: `scripts/build_acpi.py`
- Test: `tests/test_acpi.py`

**Interfaces:**
- Consumes: `deps/acpica/acpidump.exe`, `deps/acpica/iasl.exe`
- Produces:
  - `acpi_dump/dsdt.aml` e `acpi_dump/dsdt.dsl`
  - `acpi_custom/SSDT-I2C1.aml` (habilita interrupção GPIO para `\_SB.PC00.I2C1.TPD0` sem referenciar `TPL0`)

- [ ] **Step 1: Escrever o teste de validação ACPI (`tests/test_acpi.py`)**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_ssdt_i2c1_compiled_and_clean():
    dsl_path = ROOT / "acpi_custom" / "SSDT-I2C1.dsl"
    aml_path = ROOT / "acpi_custom" / "SSDT-I2C1.aml"
    assert dsl_path.is_file()
    assert aml_path.is_file() and aml_path.stat().st_size > 64
    dsl_text = dsl_path.read_text(encoding="utf-8")
    assert "_SB.PC00.I2C1.TPD0" in dsl_text
    assert "TPL0" not in dsl_text
```

- [ ] **Step 2: Rodar o teste para confirmar que falha**

Run: `pytest tests/test_acpi.py -v`
Expected: FAIL (`AssertionError`)

- [ ] **Step 3: Criar `acpi_custom/SSDT-I2C1.dsl` e implementar `scripts/build_acpi.py`**

Criar `acpi_custom/SSDT-I2C1.dsl` adaptada de `SSDT-XPS-I2C.dsl` exclusivamente para o touchpad `\_SB.PC00.I2C1.TPD0` (`DELL0B24`) no barramento `I2C1` (`0x00150001`), mantendo os métodos `XINI`/`XCRS` pareados com o rename ACPI do `config.plist`, e compilar com `deps/acpica/iasl.exe -oa acpi_custom/SSDT-I2C1.dsl`, além de extrair o DSDT do sistema em `acpi_dump/`.

- [ ] **Step 4: Executar `scripts/build_acpi.py` e rodar o teste**

Run: `python scripts/build_acpi.py && pytest tests/test_acpi.py -v`
Expected: PASS

---

### Task 3: Mapeamento USB Sob Medida (`UTBMap.kext`) para o Inspiron 15 5510 (`build_usbmap.py`)

**Files:**
- Create: `scripts/build_usbmap.py`
- Test: `tests/test_usbmap.py`

**Interfaces:**
- Produces: `acpi_custom/UTBMap.kext/Contents/Info.plist`

- [ ] **Step 1: Escrever o teste do mapa USB (`tests/test_usbmap.py`)**

```python
import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INFO = ROOT / "acpi_custom" / "UTBMap.kext" / "Contents" / "Info.plist"

def test_utbmap_valid_and_within_15_port_limit():
    assert INFO.is_file()
    data = plistlib.loads(INFO.read_bytes())
    personalities = data["IOKitPersonalities"]
    assert len(personalities) >= 1
    for name, p in personalities.items():
        assert p["model"] == "MacBookPro16,2"
        ports = p["IOProviderMergeProperties"]["ports"]
        assert len(ports) <= 15, f"{name} exceeds 15-port limit: {len(ports)}"
```

- [ ] **Step 2: Rodar o teste para confirmar que falha**

Run: `pytest tests/test_usbmap.py -v`
Expected: FAIL (`AssertionError`)

- [ ] **Step 3: Implementar `scripts/build_usbmap.py`**

Inspecionar via PnP/WMI as portas USB conectadas ao controlador PCH `\_SB.PC00.XHCI` (`8086:A0ED`, onde residem o Bluetooth Intel CNVi na porta `HS10`/`HS14` tipo `255`, webcam interna tipo `255` e portas USB-A externas tipo `3`) e ao controlador Thunderbolt `\_SB.PC00.TXHC` (`8086:9A13`, USB-C tipo `9`), gerando `acpi_custom/UTBMap.kext/Contents/Info.plist` para `MacBookPro16,2` com $\le 15$ portas por controlador.

- [ ] **Step 4: Executar `scripts/build_usbmap.py` e rodar o teste**

Run: `python scripts/build_usbmap.py && pytest tests/test_usbmap.py -v`
Expected: PASS

---

### Task 4: Gerador e Validador da EFI OpenCore 1.0.8 (`build_efi.py`)

**Files:**
- Create: `scripts/build_efi.py`
- Test: `tests/test_efi_config.py`

**Interfaces:**
- Consumes:
  - `deps/Hackintosh-XPS13Plus-IrisXe-Tahoe/EFI`
  - `deps/OcBinaryData/Drivers/HfsPlus.efi`
  - `deps/AppleALC/AppleALC.kext`
  - `acpi_custom/SSDT-I2C1.aml`
  - `acpi_custom/UTBMap.kext`
  - `deps/OpenCore-1.0.8/Utilities/macserial/macserial.exe`
  - `deps/OpenCore-1.0.8/Utilities/ocvalidate/ocvalidate.exe`
- Produces:
  - `dist/EFI/OC/config.plist` (aceleração Metal 2 ativa)
  - `dist/EFI/OC/config-install.plist` (modo VESA seguro para instalação)
  - `dist/smbios-secret.json` (backup local privado do serial gerado)

- [ ] **Step 1: Escrever os testes completos da EFI (`tests/test_efi_config.py`)**

```python
import plistlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_OC = ROOT / "dist" / "EFI" / "OC"
OCVALIDATE = ROOT / "deps" / "OpenCore-1.0.8" / "Utilities" / "ocvalidate" / "ocvalidate.exe"

def load_plist(name: str) -> dict:
    return plistlib.loads((DIST_OC / name).read_bytes())

def test_ocvalidate_passes_both_configs():
    for name in ("config.plist", "config-install.plist"):
        res = subprocess.run([str(OCVALIDATE), str(DIST_OC / name)], capture_output=True, text=True)
        assert "No issues found" in res.stdout, f"{name} failed ocvalidate:\n{res.stdout}\n{res.stderr}"

def test_xps_specific_items_removed_and_inspiron_added():
    cfg = load_plist("config.plist")
    acpi_names = [a["Path"] for a in cfg["ACPI"]["Add"] if a["Enabled"]]
    assert "SSDT-XPS-I2C.aml" not in acpi_names
    assert "SSDT-I2C1.aml" in acpi_names

    kext_paths = {k["BundlePath"]: k["Enabled"] for k in cfg["Kernel"]["Add"]}
    assert kext_paths.get("CpuTopologyRebuild.kext", False) is False
    assert kext_paths.get("UTBDefault.kext", False) is False
    assert kext_paths.get("UTBMap.kext") is True
    assert kext_paths.get("AppleALC.kext") is True
    assert kext_paths.get("NootedGreen.kext") is True

    cfg_inst = load_plist("config-install.plist")
    inst_kexts = {k["BundlePath"]: k["Enabled"] for k in cfg_inst["Kernel"]["Add"]}
    assert inst_kexts.get("NootedGreen.kext") is False

def test_nvram_boot_args_and_smbios_populated():
    nvram_guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
    for name in ("config.plist", "config-install.plist"):
        cfg = load_plist(name)
        assert "boot-args" in cfg["NVRAM"]["Delete"][nvram_guid]
        generic = cfg["PlatformInfo"]["Generic"]
        assert generic["SystemProductName"] == "MacBookPro16,2"
        assert len(generic["SystemSerialNumber"]) >= 10
        assert "CHANGE_ME" not in generic["SystemSerialNumber"]

    accel_args = load_plist("config.plist")["NVRAM"]["Add"][nvram_guid]["boot-args"]
    assert "-ngreentglwithgfx" in accel_args
    assert "ngreen-dmc=adlp" not in accel_args

    inst_args = load_plist("config-install.plist")["NVRAM"]["Add"][nvram_guid]["boot-args"]
    assert "-igfxvesa" in inst_args
```

- [ ] **Step 2: Rodar o teste para confirmar que falha**

Run: `pytest tests/test_efi_config.py -v`
Expected: FAIL (`FileNotFoundError` / `AssertionError`)

- [ ] **Step 3: Implementar `scripts/build_efi.py`**

Implementar a montagem completa de `dist/EFI`:
1. Copiar `deps/Hackintosh-XPS13Plus-IrisXe-Tahoe/EFI` para `dist/EFI`.
2. Copiar `HfsPlus.efi` para `dist/EFI/OC/Drivers/`, `AppleALC.kext` e `UTBMap.kext` para `dist/EFI/OC/Kexts/`, e `SSDT-I2C1.aml` para `dist/EFI/OC/ACPI/`.
3. Remover `SSDT-XPS-I2C.aml`, `UTBDefault.kext` e `CpuTopologyRebuild.kext`.
4. Configurar `Kernel > Emulate` para Tiger Lake (`Cpuid1Data: <65060A00 00000000 00000000 00000000>`, `Cpuid1Mask: <FFFFFFFF 00000000 00000000 00000000>` — Comet Lake/Ice Lake spoof sem o hack de 16 threads do Raptor Lake).
5. Configurar `DeviceProperties > Add`:
   - `PciRoot(0x0)/Pci(0x2,0x0)`: `AAPL,ig-platform-id = <0000499A>`, `device-id = <499A0000>`, `model = "Intel Iris Xe Graphics"`.
   - `PciRoot(0x0)/Pci(0x1F,0x3)`: `layout-id = <0B000000>` (layout 11 inicial para Realtek ALC236).
6. Configurar `boot-args`:
   - `config.plist`: `-v keepsyms=1 debug=0x100 IGLogLevel=3 -ngreentglwithgfx -allow3d -disablegfxfirmware ngreenSched=4 -ngreenxefix gfxrst=1 amfi_get_out_of_my_way=1 alcid=11`
   - `config-install.plist`: `-v keepsyms=1 debug=0x100 -igfxvesa amfi_get_out_of_my_way=1 alcid=11` (com `NootedGreen.kext` `Enabled=False`).
7. Gerar SMBIOS único com `macserial.exe -m MacBookPro16,2 -g -n 1` e gravar em ambos os `.plist` + `dist/smbios-secret.json`.

- [ ] **Step 4: Executar `scripts/build_efi.py` e rodar os testes**

Run: `python scripts/build_efi.py && pytest tests/test_efi_config.py -v`
Expected: PASS (`No issues found` no `ocvalidate.exe`)

---

### Task 5: Empacotador Offline do Stack de Aceleração Metal (`pack_macos_bundle.py`)

**Files:**
- Create: `scripts/pack_macos_bundle.py`
- Test: `tests/test_bundle.py`

**Interfaces:**
- Consumes: `deps/Hackintosh-XPS13Plus-IrisXe-Tahoe`
- Produces:
  - `dist/irisxe-tahoe-bundle.tar.gz`
  - `dist/LEIAME-INSTALACAO.md`

- [ ] **Step 1: Escrever o teste do pacote offline (`tests/test_bundle.py`)**

```python
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "dist" / "irisxe-tahoe-bundle.tar.gz"
GUIDE = ROOT / "dist" / "LEIAME-INSTALACAO.md"

def test_tarball_contains_required_macos_scripts():
    assert BUNDLE.is_file() and BUNDLE.stat().st_size > 1_000_000
    with tarfile.open(BUNDLE, "r:gz") as tf:
        names = set(tf.getnames())
        assert "Hackintosh-XPS13Plus-IrisXe-Tahoe/install.sh" in names
        assert "Hackintosh-XPS13Plus-IrisXe-Tahoe/macos/install-macos.sh" in names
        assert "Hackintosh-XPS13Plus-IrisXe-Tahoe/macos/patch-mtl17.py" in names
    assert GUIDE.is_file()
```

- [ ] **Step 2: Rodar o teste para confirmar que falha**

Run: `pytest tests/test_bundle.py -v`
Expected: FAIL (`AssertionError`)

- [ ] **Step 3: Implementar `scripts/pack_macos_bundle.py` e gerar `dist/LEIAME-INSTALACAO.md`**

Empacotar `deps/Hackintosh-XPS13Plus-IrisXe-Tahoe` em `dist/irisxe-tahoe-bundle.tar.gz` (preservando permissões de execução `.sh` e excluindo `.git` desnecessário se quiser economizar espaço, ou mantendo `.git` para permitir `git pull` no macOS) e gerar `dist/LEIAME-INSTALACAO.md` com os comandos exatos de pós-instalação no macOS.

- [ ] **Step 4: Executar `scripts/pack_macos_bundle.py` e rodar o teste**

Run: `python scripts/pack_macos_bundle.py && pytest tests/test_bundle.py -v`
Expected: PASS

---

### Task 6: Script Seguro de Particionamento Dual-Boot e Criação do Pendrive (`prepare_dualboot.ps1`)

**Files:**
- Create: `scripts/prepare_dualboot.ps1`
- Test: `tests/test_dualboot_script.py`

**Interfaces:**
- Consumes: `dist/EFI`, `dist/irisxe-tahoe-bundle.tar.gz`, `dist/LEIAME-INSTALACAO.md`
- Produces: Script PowerShell validado com modo `--DryRun` (`-WhatIf`) para:
  1. Verificar status do BitLocker em `C:`.
  2. Reduzir `C:` em 128 GB (`Resize-Partition -DriveLetter C`) deixando 128 GB livres para o APFS do macOS.
  3. Preparar o pendrive USB com `EFI/OC/config-install.plist` ativo como `config.plist` (para o 1º boot) + `config-accelerated.plist` guardado + `irisxe-tahoe-bundle.tar.gz`.

- [ ] **Step 1: Escrever o teste de sintaxe e segurança do script PowerShell (`tests/test_dualboot_script.py`)**

```python
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS_SCRIPT = ROOT / "scripts" / "prepare_dualboot.ps1"

def test_powershell_script_dry_run_succeeds():
    assert PS_SCRIPT.is_file()
    res = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(PS_SCRIPT), "-DryRun"],
        capture_output=True, text=True
    )
    assert res.returncode == 0, res.stderr
    assert "DRY-RUN OK" in res.stdout
```

- [ ] **Step 2: Rodar o teste para confirmar que falha**

Run: `pytest tests/test_dualboot_script.py -v`
Expected: FAIL (`AssertionError`)

- [ ] **Step 3: Implementar `scripts/prepare_dualboot.ps1`**

Implementar `scripts/prepare_dualboot.ps1` com parâmetros `-DryRun`, `-ShrinkDisk` e `-UsbDriveLetter`, verificações de espaço livre no volume `C:`, checagem de `dist/EFI/OC/config-install.plist`, e cópia automatizada para o pendrive.

- [ ] **Step 4: Rodar toda a suíte de testes (`pytest`)**

Run: `pytest -v`
Expected: Todos os testes passando (`test_deps.py`, `test_acpi.py`, `test_usbmap.py`, `test_efi_config.py`, `test_bundle.py`, `test_dualboot_script.py`).
