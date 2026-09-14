# Review Context Workflow

Shared procedure for all C code review skills. Perform this as Step 0 before any review work.

## Step 0: Collect Review Context and Record Start Time

Read git metadata — `git` is spelled the same in every shell, so these lines are literal:

```
git rev-parse --abbrev-ref HEAD          # branch name
git rev-parse --short HEAD               # commit hash
git log -1 --format="%an"                # commit author
```

Then note the current wall-clock time as `HH:MM:SS` for `Review Start`, using whatever your shell
offers (`Get-Date -Format "HH:mm:ss"` in PowerShell, `date +%H:%M:%S` in bash).

Extract from the branch name:
- **Branch type**: prefix before the first `/` (e.g. `feature`, `fix`, `refactor`, `chore`, `hotfix`)
- **Jira ticket**: first match of pattern `[A-Z]+-\d+` in the branch name (e.g. `PROJ-123`)
- If no Jira ticket is found, write `N/A`

Fill `Review Start` and git metadata into the protocol header immediately.

If a component path is provided, enumerate every `.c` and `.h` file under it **recursively** and
pre-populate **Files Reviewed** in the protocol header — with the tool or shell command of your
choice, the result is what matters.

List every file by its relative path from the repository root. Add any additional files opened during the review.

## Protocol Header Template

Use this table as the header for every review protocol:

| Field              | Value                                                  |
|--------------------|--------------------------------------------------------|
| **Component**      | `<component_name>`                                     |
| **Date**           | [YYYY-MM-DD]                                           |
| **Review Start**   | [HH:MM:SS]                                             |
| **Review End**     | [HH:MM:SS]                                             |
| **Duration**       | [HH:MM:SS]                                             |
| **Reviewer**       | [reviewer name / AI model]                             |
| **Git Branch**     | [branch name]                                          |
| **Commit Hash**    | [short hash]                                           |
| **Commit Author**  | [author name]                                          |
| **Jira Ticket**    | [TICKET-XXX or N/A]                                    |
| **Branch Type**    | [feature / fix / refactor / chore / hotfix / ...]      |
| **Files Reviewed** | List every individual file that was opened and read (one per line): `path/to/file.c`, `path/to/file.h`, ... |

## Recording End Time

At the end of every review, note the wall-clock time again, the same way as in Step 0.

Calculate the duration and fill `Review End` and `Duration` into the protocol header before saving the report.
