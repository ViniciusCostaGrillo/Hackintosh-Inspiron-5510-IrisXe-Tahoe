# 07 — Base de Conhecimento Completa: Engenharia Hackintosh Tiger Lake & Intel Iris Xe Metal

> **Notebook Alvo:** Dell Inspiron 15 5510  
> **Processador:** 11ª Geração Intel Core i5-11320H (Tiger Lake-H35, 4 Cores / 8 Threads, 3.20 GHz até 4.50 GHz, Willow Cove)  
> **Gráficos Integrados:** Intel Iris Xe Graphics G7 (96 Execution Units, Device ID `8086:9A49`, Subsystem `1028:0A54`)  
> **Controlador de Armazenamento:** SSD NVMe ADATA `SM2P41C3` 256 GB (Silicon Motion SM2263XT DRAM-less, `1CC1:41C3`)  
> **Rede Sem Fio:** Intel Wi-Fi 6 AX201 160MHz (CNVi, `8086:A0F0`) + Bluetooth 5.2 (`8087:0026`)  
> **Touchpad:** I2C HID Dell (`DELL0B24`, endereço `0x2C` em `\_SB.PC00.I2C1.TPD0`)  
> **Áudio:** Realtek ALC236 (`10EC:0236`, Layout-ID 11)  
> **Bootloader:** OpenCore 1.0.8 RELEASE  
> **Sistema Operacional Alvo:** macOS Tahoe 26.7.1 (Build `25G241`)  

---

## 1. O Desafio Histórico da 11ª Geração (Tiger Lake)

Durante anos, a comunidade Hackintosh considerou a 11ª Geração Intel (Tiger Lake) **impossível de rodar macOS com aceleração**, por duas razões estruturais:

1. **Inexistência de Mac Oficial Tiger Lake:**  
   A Apple realizou a transição direta da 10ª Geração (Ice Lake / Comet Lake) para os processadores próprios Apple Silicon (M1). Nenhum Mac oficial foi lançado com CPU Tiger Lake ou GPU Iris Xe.
2. **Arquitetura Gráfica Gen12 (Intel Xe-LP):**  
   A microarquitetura Gen12 representou um salto total em relação à Gen11 (Ice Lake). Ela introduziu novas filas de comando de anel, pipelines de display engine (Display 12), gerenciamento de cache L3 e um novo conjunto de instruções de shader que os drivers antigos da Apple (`AppleIntelICLLPGraphics`) não sabem interpretar.

### A Descoberta dos Drivers Protótipo da Apple e o Ecossistema WhateverXe
* **A Descoberta:** Em builds de desenvolvimento da Apple e protótipos de transição, a engenharia da Apple desenvolveu internamente o conjunto `GPUDriversIntel 16.0.32` com suporte prévio à arquitetura Tiger Lake (`AppleIntelTGLGraphics*`).
* **Engenharia Reversa (NootedGreen & b00t0x):**  
  Projetos como `NootedGreen` e, mais recentemente, **`WhateverXe`** (desenvolvido por *b00t0x*) adaptaram e reconstruíram esses binários para sistemas modernos (macOS Sequoia e macOS Tahoe 26.7.1 `25G241`), permitindo aceleração gráfica total via Metal 2 e Metal 3.

---

## 2. A Arquitetura em 2 Fases (Regra de Ouro)

A aceleração de Iris Xe **nunca** pode estar habilitada durante o boot do instalador da Apple (`BaseSystem.dmg`).

| Fase | Ambiente | Driver Gráfico | Boot-args Principais | Kexts Gráficas |
|---|---|---|---|---|
| **Fase 1: Instalação** | Recuperação / Instalador (`BaseSystem.dmg` - Read-Only) | Modo VESA seguro (CPU Framebuffer) | `-v keepsyms=1 debug=0x100 -vi2c-force-polling -igfxvesa` | `WhateverGreen.kext` (Ativa)<br>`WhateverXe.kext` (Desativada)<br>`NootedGreen.kext` (Desativada) |
| **Fase 2: Pós-Instalação** | macOS Instalado no SSD (`Macintosh HD` - Gravável) | Aceleração Metal 2/3 Nativa | `-v keepsyms=1 debug=0x100 -vi2c-force-polling -igfxdvmt amfi_get_out_of_my_way=1 ipc_control_port_options=0 alcid=11` | `WhateverXe.kext` (Ativa)<br>`AMFIPass.kext` (Ativa)<br>`WhateverGreen.kext` (Desativada) |

> **Por quê?**  
> Os componentes de user-space da GPU (`.bundle`, `libxedrv.dylib` e shaders compilados) precisam ser instalados em `/Library/GPUBundles` na raiz gravável do sistema operacional. Se o kernel tentar inicializar o driver acelerado dentro do instalador (onde esses arquivos não existem), o sistema trava instantaneamente em `spec_open` ou `IOAccelerator`.

---

## 3. Matriz de Falhas, Causa-Raiz e Soluções Definitivas

Durante o processo de calibração do Dell Inspiron 15 5510, 8 obstáculos críticos foram diagnosticados e resolvidos:

### Falha 1: Congelamento Imediato no Kernel Bootstrapper (`#[EB|LOG:EXITBS:START]`)
* **Sintoma:** O boot parava imediatamente após a saída dos serviços de boot UEFI.
* **Causa-Raiz:** O Dell Inspiron 15 5510 protege áreas vitais de memória física (MMIO) no barramento PCI e firmware da BIOS. Sem acesso em tempo de execução, o kernel do macOS entrava em pânico.
* **Solução:** Whitelist das regiões MMIO específicas do Tiger Lake em `Booter > MmioWhitelist`:
  * `0xC0000000` (PCIe ECAM / MCFG)
  * `0xFD000000` (PCH SBREG)
  * `0xFE000000` (PMC / P2SB)
  * `0xFE010000` (SPI BAR0 NVRAM)
  * `0xFED00000` (HPET / VT-d)
  * `0xFEE00000` (Local APIC)
  * `0xFF000000` (Flash ROM da BIOS)

---

### Falha 2: Erro ACPI `\_SB.EPC._CRS returned invalid address`
* **Sintoma:** O ACPI Interpreter falhava e reiniciava o notebook em loop.
* **Causa-Raiz:** O patch genérico de renomear `_STA to XSTA` em `GPI0` estava sem limite de contagem (`Count=0`), o que renomeava indevidamente o método `_STA` do dispositivo `_SB.EPC` (Intel SGX Enclave Page Cache). Como resultado, o `_CRS` do EPC retornava `0xFFFFFFFFFFFFFFFF`.
* **Solução:** Restringir o patch `GPI0 _STA to XSTA` para `Count = 1`, aplicando-o exclusivamente ao controlador GPIO de hardware sem corromper o EPC.

---

### Falha 3: Kernel Panic por Divisão por Zero (`idiv r8d` em `0x1a8a`)
* **Sintoma:** Pânico de kernel instantâneo nos primeiros milissegundos após carregar os módulos.
* **Causa-Raiz:** Uso da kext `CpuTopologyRebuild.kext`. Essa kext foi criada para arquiteturas híbridas (Alder Lake / Raptor Lake) que possuem núcleos de performance (P-Cores) e núcleos de eficiência (E-Cores). No Core i5-11320H do Inspiron 5510, a CPU possui **4 P-Cores e 0 E-Cores**. Ao tentar dividir a carga pelo número de E-Cores (`0`), a instrução assembly `idiv r8d` causava interrupção de divisão por zero.
* **Solução:** Remover completamente `CpuTopologyRebuild.kext`. CPUs Tiger Lake são homogêneas e utilizam nativamente `SSDT-PLUG.aml` + `VirtualSMC`.

---

### Falha 4: Travamento USB e Pânico de DMAR / RMRR
* **Sintoma:** Portas USB não respondiam ou ocorria pânico na inicialização do subsistema IOMMU/AppleVTD.
* **Causa-Raiz:** 
  1. O arquivo OEM `DMAR` da BIOS da Dell continha regiões reservadas de memória (RMRR de `0x6C000000` até `0x707FFFFF`), incompatíveis com a paginação do AppleVTD.
  2. Uso de `XHCI-unsupported.kext`, que sequestrava o Device ID `0xA0ED` da Tiger Lake e tentava forçar o driver antigo `AppleUSBXHCISPT` de Skylake.
* **Solução:**
  1. Descartar a tabela OEM DMAR (`ACPI > Delete > DMAR`) e injetar uma tabela limpa compilada sem RMRR (`acpi_custom/DMAR.aml`).
  2. Remover `XHCI-unsupported.kext` e mapear as 14 portas reais (11 portas em `XHCI` + 3 em `TXHC` Thunderbolt) usando `UTBMap.kext`.

---

### Falha 5: Falha do Controlador NVMe ADATA (`AppleNVMe Assert failed: ReleaseIDNode`)
* **Sintoma:** Mensagens contínuas no verbose:
  ```text
  AppleNVMe Assert failed: (0 != data) ReleaseIDNode ...
  AppleNVMe Assert failed: kIOReturnSuccess == (status) Exit file: ... IONVMeController.cpp line: 6115
  ```
  Seguido de parada na criação da fila de submissão do disco (`CreateSubmissionQueue`).
* **Causa-Raiz:** O SSD ADATA SM2P41C3 utiliza o controlador **Silicon Motion SM2263XT** (DRAM-less). Quando o driver de gerenciamento de energia da Apple tenta colocar o SSD em estados APST (Autonomous Power State Transition) ultra-profundos ou envia comandos de TRIM assíncronos não suportados, o chip SM2263XT trava o barramento PCIe.
* **Solução:**
  1. Habilitar `NVMeFix.kext` (versão 1.1.4) no `config.plist`.
  2. Configurar `SetApfsTrimTimeout = -1` em `Kernel > Quirks` para prevenir stalls de TRIM no boot.

---

### Falha 6: Travamento em `spec_open` com `-wegnoigpu`
* **Sintoma:** O boot congelava na linha:
  ```text
  spec_open : si_devbsdunit initialized to (0), throttle_mask is (0x1), lsssd is (0)
  ```
* **Causa-Raiz:** Ao passar a flag `-wegnoigpu` em um notebook que **não possui placa de vídeo dedicada (dGPU)**, o WhateverGreen desativava completamente a única GPU existente (a Iris Xe). Quando o subsistema BSD tentava inicializar a saída de console de vídeo primária (`spec_open` no dispositivo de console), ele encontrava um barramento nulo e congelava aguardando um framebuffer.
* **Solução:** Remover `-wegnoigpu` e utilizar a flag canônica de compatibilidade: **`-igfxvesa`**. O `-igfxvesa` mantém o dispositivo gráfico ativo no PCI, mas impede que qualquer driver acelerado tente carregar, operando com o framebuffer básico da EFI.

---

### Falha 7 (O GRANDE DESCOBRIMENTO): Congelamento no `[1(launchd)] check` / `libignition`
* **Sintoma:** O sistema montava o `BaseSystem.dmg`, carregava o launchd e congelava exatamente em:
  ```text
  shared_region: 0x... [1(launchd)] check_np(...) returned 0x1
  Darwin Ignition Sequence Version 1.0.0 ...
  libignition arguments :
  ```
* **Causa-Raiz:** O arquivo de configuração herdado de outros repositórios continha:
  * `Cpuid1Data`: `55060A00 00008000 00000000 00000000`
  * `Cpuid1Mask`: `FFFFFFFF 0000FF00 00000000 00000000`
  O byte `0x80` em `EBX[23:16]` representa uma máscara de contagem de threads de arquitetura Alder Lake (com 12 threads repartidas entre P-cores e E-cores). O kernel do macOS, ao carregar a biblioteca de inicialização do Darwin (`libignition`), tentava ler os limites de topologia desse registrador forçado. Ao detectar uma incompatibilidade com a tabela ACPI de 4 núcleos homogêneos (`_SB.PR00` a `_SB.PR07`), a rotina de sincronização de threads entrava em dead-lock eterno.
* **Solução Definitiva:**
  Aplicar o spoof limpo padrão de Comet Lake para CPUs de 4 núcleos:
  * **`Cpuid1Data`:** `55060A00 00000000 00000000 00000000`
  * **`Cpuid1Mask`:** `FFFFFFFF 00000000 00000000 00000000`
  Imediatamente após essa correção, o `libignition` liberou o agendamento de threads e a interface gráfica da Recuperação do macOS abriu perfeitamente!

---

## 4. O Bloqueio de DVMT da Dell e Como o WhateverXe Resolve

A Dell bloqueia em firmware a memória de vídeo pré-alocada (DVMT Pre-Allocated) em **32 MB ou 60 MB** em notebooks Inspiron e XPS, sem opção de ajuste visual na interface da BIOS.

* O driver de aceleração gráfica da Apple espera um mínimo de **96 MB** de DVMT.
* Sem tratamento, ao tentar carregar o driver acelerado, o sistema congela com *kernel panic* ou tela preta.

### A Solução no `config-whateverxe.plist`:
1. **Boot-arg `-igfxdvmt`:** Instrui a kext `WhateverXe.kext` a contornar as asserções de tamanho de DVMT no código binário do driver.
2. **Propriedades injetadas em `PciRoot(0x0)/Pci(0x2,0x0)`:**
   * `framebuffer-patch-enable` = `01000000` (Data)
   * `framebuffer-stolenmem` = `0000C003` (Data: 60 MB alocados para compensação)
   * `framebuffer-fbmem` = `00000003` (Data: 48 MB de framebuffer)
   * `enable-metal` = `01000000` (Data: Ativação explícita de pipelines Metal)

---

## 5. Conectividade de Rede no Instalador

Como o macOS Tahoe não possui drivers nativos para placas Wi-Fi modernas da Intel:

1. **Método Plug-and-Play (Samsung Galaxy A55 via USB Tethering):**
   * Conecte o cabo USB do smartphone no Dell Inspiron 5510.
   * No celular, vá em **Configurações > Conexões > Roteador Wi-Fi e Ancoragem > Ancoragem via USB**.
   * O macOS reconhece a conexão imediatamente como adaptador Ethernet com fio (`en1`), baixando os pacotes sem requerer digitação de senhas.
2. **Método Wi-Fi com `itlwm.kext`:**
   * A `itlwm.kext` já está incluída e ativa no `config.plist`. Ela emula uma placa de rede Ethernet virtual (`en0`).
   * No pós-instalação, pode ser utilizado o utilitário **HeliPort** ou os patches do **OpenCore Legacy Patcher** para controle gráfico de redes Wi-Fi.

---

## 6. Procedimento de Ativação Gráfica Metal Pós-Instalação

Assim que a instalação do macOS Tahoe for concluída e você chegar na Área de Trabalho:

### Passo 1: Instalação do Pacote Gráfico
No terminal do macOS (ou pelo Finder dando duplo-clique no arquivo no pendrive):
```zsh
sudo installer -pkg /Volumes/HACKINTOSH/WhateverXe-Graphics-0.4.4.pkg -target /
```

### Passo 2: Ativação da Configuração Acelerada
```zsh
cp /Volumes/HACKINTOSH/EFI/OC/config-whateverxe.plist /Volumes/HACKINTOSH/EFI/OC/config.plist
sync
```

### Passo 3: Autorização de Segurança e Cache
1. Abra **Ajustes do Sistema > Privacidade e Segurança**.
2. Clique em **Permitir (Allow)** ao lado da extensão bloqueada.
3. No Terminal:
   ```zsh
   sudo kmutil install --volume-root / --update-all --force
   ```
4. Reinicie o notebook.

### Passo 4: Validação
No Terminal:
```zsh
system_profiler SPDisplaysDataType
```
Deverá constar:
* **Chipset Model:** `Intel Iris Xe Graphics`
* **VRAM (Total):** `1536 MB`
* **Metal Support:** `Metal 2` / `Metal 3`

---

## 7. Referência de Comandos e Utilitários Úteis

| Ação | Comando / Caminho | Finalidade |
|---|---|---|
| **Verificar versão e build** | `sw_vers` | Confirma se a build é `25G241` |
| **Validar aceleração Metal** | `system_profiler SPDisplaysDataType` | Exibe modelo da GPU, VRAM e versão do Metal |
| **Montar EFI interna do SSD** | `sudo diskutil mount disk0s1` | Permite migrar a EFI do pendrive para o SSD interno |
| **Desativar suspensão profunda** | `sudo pmset -a hibernatemode 0 sleep 0 loads 0` | Mantém o notebook seguro contra bugs de S3 Sleep |
| **Reconstruir cache de kexts** | `sudo kmutil install --volume-root / --update-all --force` | Atualiza a Auxiliary Kernel Collection (AKC) |
