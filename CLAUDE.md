<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## OpenSpec Apply Workflow

When running `/openspec:apply`:

### Step 1: Discover and Display Proposals

1. Find all proposals in `openspec/changes/` (exclude `archive/`)
2. For each proposal, check git status to determine if it has uncommitted changes:
   - `??` (untracked), `M` (modified), `A` (staged), `AM` (added+modified) = uncommitted
3. Read each `proposal.md` to get a brief description
4. Display all proposals with their status:

```
Available proposals:

1. add-demo-apps ✓ (committed)
   Brief description from proposal.md

2. refactor-launcher-lazy-load ✗ (uncommitted)
   Brief description from proposal.md
```

### Step 2: Handle Based on What's Available

**If all proposals have uncommitted changes:**
- STOP and tell the user which proposals need to be committed
- Provide the git commands to commit them:
  ```
  git add openspec/changes/<id>/
  git commit -m "Add <id> proposal"
  ```

**If one or more proposals are fully committed:**
- Ask the user which one to apply (always confirm, even if there's only one)

### Step 3: Pre-Implementation Checks

1. **Assess context needs** - Check remaining context window and read the plan complexity (tasks.md). If context is low (<50% remaining) or the plan is complex, recommend the user run `/clear` first and re-run the command.

### Step 4: Set Up Worktree and Implement

1. Create a new git worktree with a branch named after the change-id:
   ```
   git worktree add ../cardputer-<change-id> -b <change-id>
   ```
2. Change to the new worktree directory
3. Run `uv sync` to create the venv
4. Run `direnv allow` to enable the environment
5. Run `uv run pre-commit install` to set up git hooks
6. Implement the changes following the tasks.md checklist

## OpenSpec Archive Workflow

When running `/openspec:archive`:

1. Run `openspec list` to check task completion status
2. **If there are incomplete tasks**: STOP and ask the user before proceeding
   - Show which tasks are incomplete
   - Ask if they want to complete them first or archive anyway
3. Only run `openspec archive <id> --yes` after user confirms

## Commit Message Style

Use conventional commit format: `<type>: <description>`

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature or functionality |
| `fix` | Bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, whitespace (no code logic change) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Build system or dependencies (PlatformIO, libs) |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance tasks, tooling |
| `revert` | Reverting a previous commit |
| `openspec` | Proposals, specs, and archives |

### Subject Line Rules

- **Imperative mood**: `add feature` not `added` or `adds`
- **Lowercase after type**: `feat: add settings app` not `feat: Add Settings App`
- **No trailing period**: `fix: resolve memory leak` not `fix: resolve memory leak.`
- **Under 50 characters**: keep it concise
- **Be specific**: `fix: prevent crash on empty config` not `fix: bug`

### Words to Avoid

- comprehensive, various, some, minor, miscellaneous, stuff, things
- Either be specific or remove the filler word entirely

### Verb Choices

| Action | Verbs |
|--------|-------|
| New feature | `add`, `implement`, `create` |
| Modify existing | `update`, `change`, `improve` |
| Remove | `remove`, `delete`, `drop` |
| Fix | `fix`, `resolve`, `correct` |
| Rename/move | `rename`, `move`, `relocate` |

### Examples

```
feat: add WiFi auto-connect on boot
fix: resolve hot-reload app selector reference
openspec: add wifi-boot-connect proposal
openspec: archive add-ftp-server
docs: update OpenSpec apply workflow
refactor: modularize settings app architecture
chore: add pre-commit hooks with gitleaks
```

### Commit Body

The body is optional but useful for non-trivial changes.

**Rules:**
- Blank line after subject (required separator)
- Wrap at 72 characters
- Explain *what* and *why*, not *how*
- Use `-` for bullet points
- Reference issues/PRs at the bottom

**When to include a body:**
- Breaking changes
- Non-obvious reasoning
- Trade-off decisions
- Context for future readers

**Example with body:**

```
feat: add WiFi auto-connect on boot

Automatically connects to saved networks when device powers on.
Reduces manual setup steps for users who frequently restart.

- Check saved credentials in NVS on boot
- Retry connection 3 times before giving up
- Fall back to AP mode if all networks fail

Closes #42
```

**Simple commits don't need a body:**

```
fix: typo in settings label
style: format with ruff
chore: update platformio to 6.1
```