# Key Facts Template

This file demonstrates the format for storing project constants, configuration, and frequently-needed **non-sensitive** information. Organize by category using bullet lists.

## ⚠️ SECURITY WARNING: What NOT to Store Here

**NEVER store passwords, API keys, or sensitive credentials in this file.** This file is typically committed to version control and should only contain non-sensitive reference information.

**❌ NEVER store:**

- Passwords or passphrases
- License keys for commercial toolchains (IAR, Keil)
- JTAG/SWD debug authentication keys
- Signing keys for secure boot
- Private keys or certificates
- CI/CD tokens or secrets

**✅ SAFE to store:**

- MCU part numbers and revision info
- Toolchain names and version numbers
- Memory map (flash/RAM base addresses and sizes)
- Communication protocol parameters (baud rates, CAN IDs)
- Pin assignments and peripheral mappings
- Build configuration names and variant identifiers
- JIRA project keys and Confluence space URLs
- Repository URLs and branch naming conventions

**Where to store secrets:**

- Hardware Security Module (HSM) or Secure Element on target
- CI/CD secret variables (GitHub Secrets, Jenkins Credentials)
- Password managers (team vault)
- Environment variables (not committed to repo)

## Format

Organize information into logical categories:

- Target hardware specifications
- Toolchain and build system configuration
- Communication interfaces (CAN, SPI, UART, etc.)
- Memory layout
- Important URLs and documentation links
- Development environment setup

Use bullet lists for simplicity and easy scanning.

## Example Structure

### Target Hardware

**MCU:**

- Part Number: `STM32F446RET6`
- Core: ARM Cortex-M4 with FPU
- Clock: 180 MHz (HSE 8 MHz crystal, PLL configured in `system_clock.c`)
- Flash: 512 KB (sectors 0-7, see linker script for layout)
- RAM: 128 KB SRAM + 64 KB CCM (stack/heap in SRAM, DMA buffers excluded from CCM)

**Board:**

- PCB Revision: Rev C (production), Rev B (legacy prototypes)
- Debugger: SEGGER J-Link EDU, SWD interface on connector J3
- Power Supply: 3.3 V regulated, 5 V input via USB or external

### Toolchain & Build System

**Compiler:**

- Toolchain: GCC ARM Embedded 12.3.1 (arm-none-eabi-gcc)
- C Standard: C11 (with MISRA C:2012 subset enforced by Polyspace)
- Optimization: `-O2` for release, `-Og` for debug
- Warnings: `-Wall -Wextra -Werror` (zero warnings policy)

**Build System:**

- Generator: CMake 3.26+
- Build tool: Ninja
- Variants: `Debug`, `Release`, `RelWithDebInfo`
- Build command: `cmake --preset release && cmake --build --preset release`

**Static Analysis:**

- Polyspace Bug Finder Server 24.2
- Polyspace Code Prover (safety-critical modules only)
- Cppcheck 2.13 (secondary, fast local checks)

### Communication Interfaces

**CAN Bus:**

- Protocol: CAN 2.0B (extended frames)
- Bitrate: 500 kbit/s
- Node ID: `0x10` (configurable via `can_cfg.h`)
- Message database: `doc/can_matrix.dbc`
- RX FIFO: CAN1 peripheral, FIFO0 with 3-deep hardware filter

**UART Debug Console:**

- Peripheral: USART2
- Baud: 115200, 8N1
- TX Pin: PA2, RX Pin: PA3
- Used for: diagnostic output, CLI commands in debug builds

### Memory Layout (from linker script)

| Region | Start | Size | Purpose |
|--------|-------|------|---------|
| FLASH Boot | 0x08000000 | 16 KB | Bootloader |
| FLASH App | 0x08004000 | 480 KB | Application |
| FLASH Config | 0x08078000 | 16 KB | NVM parameter storage |
| SRAM | 0x20000000 | 128 KB | Heap, stack, .bss, .data |
| CCM RAM | 0x10000000 | 64 KB | RTOS stacks (no DMA access) |

### Development Environment

**Required tools (installed via `scoopfile.json`):**

- CMake, Ninja, arm-none-eabi-gcc
- OpenOCD (flashing and debug)
- Python 3.11+ (build scripts, code generation)

**Debug:**

- IDE: VS Code with Cortex-Debug extension
- GDB Server: OpenOCD or J-Link GDB Server
- SVD File: `STM32F446.svd` (register viewer)

### Important URLs

> **Note:** Do not guess or invent URLs. Ask the user for the actual links relevant to their project. Typical categories to ask about:

- Documentation portal (SharePoint, Confluence, Wiki)
- CI/CD system (Jenkins, GitLab CI)
- Artifact repository (Artifactory, Nexus)
- Issue tracker (Jira board URL)
- Static analysis dashboard (Polyspace Access URL)

## Tips

- Keep entries current (update when hardware revisions change or toolchain is upgraded)
- Remove deprecated information after migration is complete
- Include both target and host development details
- Mark deprecated items clearly with dates
- Reference linker map file for exact memory usage after each release
