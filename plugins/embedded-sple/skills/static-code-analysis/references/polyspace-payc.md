# Polyspace As You Code (PAYC) Workflow

Tool-specific workflow for running Polyspace As You Code via the VS Code extension.

## Table of Contents

- [Step P1: Verify Options File Exists](#step-p1-verify-options-file-exists)
- [Step P2: Analyze Existing Polyspace Comments](#step-p2-analyze-existing-polyspace-comments)
- [Step P3: Request User to Run Analysis](#step-p3-request-user-to-run-analysis) (**blocking**)
- [Step P4: Retrieve Findings](#step-p4-retrieve-findings)
- [VS Code Extension Commands Reference](#vs-code-extension-commands-reference)
- [MISRA Rule Classification](#misra-rule-classification)
- [Common Polyspace Checks](#common-polyspace-checks)
- [Polyspace Justification Comment Examples](#polyspace-justification-comment-examples)

> **Prerequisites**: 
> - Polyspace As You Code VS Code extension installed (MathWorks)
> - Access to Polyspace Access server (if baseline comparison is needed)
> - PAYC options file generated: `build/sca_ps_payc_options_file.txt`

## Step P1: Verify Options File Exists

```powershell
# Check if PAYC options file exists
Test-Path ./build/sca_ps_payc_options_file.txt
```

If the file doesn't exist, generate it:

> **BUILD**: Invoke the `build-execution` skill to generate the options file.
> The exact command depends on your project's static analysis tooling. Typical pattern:
> ```
> <static-analysis-tool> generate-ps-options-file --project-root-dir $PWD --variant <VARIANT> --build-kit prod --build-type Debug --payc --output-folder ./build
> ```

**Variants**: Use the variant names configured in your project (see `variants/` directory or `.vscode/cmake-variants.json`).

## Step P2: Analyze Existing Polyspace Comments

Search for existing justification comments in source code:

```powershell
# Find existing polyspace comments in component
Select-String -Path "components/<component>/**/*.c" -Pattern "polyspace" -Recurse
```

**Polyspace comment formats:**
- `/* polyspace +1 <CHECK>:<IMPACT> <JUSTIFICATION_TEXT> */` - Justify next line
- `/* polyspace:begin <CHECK>:<IMPACT> */` - Begin block justification
- `/* polyspace:end <CHECK>:<IMPACT> */` - End block justification

## Step P3: Request User to Run Analysis

> 🚫 **BLOCKING STEP — DO NOT SKIP**
>
> Existing IDE diagnostics (`ide-get_diagnostics`) may reflect a previous analysis run and
> **MUST NOT be used** without first requesting a fresh analysis from the user. Stale results
> can miss new findings or reference code that has changed since the last run.
>
> **STOP here** and use `ask_user` to request a fresh analysis:
>
> > Please run a fresh Polyspace analysis now:
> > 1. Open a `.c` file from the component in the editor
> > 2. Right-click → **"Run Polyspace Analysis"** (or Command Palette: `Polyspace: Analyze File`)
> > 3. Wait until the analysis completes (status bar shows "Analysis done")
> > 4. Confirm here when finished
>
> **Do NOT proceed to Step P4 until the user explicitly confirms the analysis is complete.**

## Step P4: Retrieve Findings

Only after the user has confirmed that a fresh analysis has completed, retrieve findings:

```text
get_errors(filePaths: ["components/<component>/src/"])
```

Polyspace findings appear as errors/warnings in the VS Code Problems panel.

## VS Code Extension Commands Reference

| Command | Description |
|---------|-------------|
| `polyspace.analyzeFile` | Analyze current file (requires file open) |
| `polyspace.addFolderToMonitoringList` | Add folder to monitoring |
| `polyspace.launchAllAnalyses` | Run all pending analyses |
| `polyspace.stopPendingAnalyses` | Stop running analyses |
| `polyspace.clearMonitoringList` | Clear monitoring list |
| `polyspace.downloadBaseline` | Download baseline from Access |

## MISRA Rule Classification

| Level         | Description                               | Handling                  |
|---------------|-------------------------------------------|---------------------------|
| **Mandatory** | Must be followed, no deviation allowed    | Always fix                |
| **Required**  | Must be followed unless formally deviated | Fix or document deviation |
| **Advisory**  | Should be followed where practical        | Consider fixing           |

## Common Polyspace Checks

- **NIV** (Non-Initialized Variable): Variable used before initialization
- **DIV** (Division by Zero): Potential division by zero
- **OVFL** (Overflow): Arithmetic overflow
- **NTC** (Non-Terminating Call): Function may not return
- **NTL** (Non-Terminating Loop): Loop may not terminate
- **UNR** (Unreachable Code): Code that cannot be executed
- **COR** (Correctness Condition): Data flow issue

## Polyspace Justification Comment Examples

```c
/* polyspace +1 MISRA-C3:11.3 [Justified:Low] Cast required for hardware register access */
volatile uint32_t* reg = (volatile uint32_t*)0x40000000;

/* polyspace:begin DEFECT:NULL_PTR [No action planned:Low] Pointer validated by caller */
void process_data(uint8_t* data) {
    // ... code ...
}
/* polyspace:end DEFECT:NULL_PTR */
```
