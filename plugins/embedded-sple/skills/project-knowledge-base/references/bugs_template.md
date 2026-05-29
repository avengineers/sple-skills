# Bug Log Template

This file demonstrates the format for logging bugs and their solutions. Keep entries brief and chronological.

## Format

Each bug entry should include:

- Date (YYYY-MM-DD)
- Brief description of the bug/issue
- Solution or fix applied
- Any prevention notes (optional)

Use bullet lists for simplicity. Older entries can be manually removed when they become irrelevant.

## Example Entries

### 2025-03-10 - Stack Overflow in CAN Receive ISR

- **Issue**: Watchdog reset during high CAN bus load
- **Root Cause**: Local buffer array in ISR consumed 512 bytes on a 1 KB ISR stack
- **Solution**: Moved buffer to static module-level variable, reduced ISR stack usage to 128 bytes
- **Prevention**: Never declare large local arrays in ISR context; use static or global buffers

### 2025-03-14 - Linker Error: Multiple Definition of `g_SystemState`

- **Issue**: Build fails with "multiple definition" error after adding new module
- **Root Cause**: Global variable defined in header file without `extern` keyword, included by 3 translation units
- **Solution**: Added `extern` in header, moved definition to `system_state.c`
- **Prevention**: Always use extern declarations in headers; define variables in exactly one .c file

### 2025-03-18 - RTOS Task Deadlock During Flash Write

- **Issue**: System hangs when saving configuration to internal flash
- **Root Cause**: Flash write disables interrupts, blocking the RTOS tick — mutex holder can never release
- **Solution**: Moved flash operations to the idle task with lowest priority and cooperative scheduling
- **Prevention**: Never perform blocking flash operations from tasks that hold shared mutexes

## Tips

- Keep descriptions under 2-3 lines
- Focus on what was learned, not exhaustive details
- Include enough context for future reference
- Date entries so you know how recent the issue is
- Periodically clean out very old entries (6+ months)
