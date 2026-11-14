# PaperSpine managed installation

When working from an installed Skill, read the adjacent `installation.json` with the manager path. Before a new PaperSpine run, use this command with the installed path and Skill root listed there:

```text
python -B "<manager>" --skills-root "<skills_root>" preflight
```

A full run checks once. A directly invoked stage checks once before loading its method. If the manager reports `updated`, reread the applicable installed instructions and use the same research files. If the chosen edition no longer offers that stage, continue with the full-paper entry and its bundled method when applicable. An offline check can continue with the existing files. If activation failed, report the failure and check the manager's resulting state before using an installed version.

Manual copy installations can work directly from their files. The user can manage updates and removal with the installer distributed alongside the three editions.
