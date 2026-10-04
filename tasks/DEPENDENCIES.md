# Task dependencies (spec §15.1, authoritative)

Generated from the task headers in this directory and cross-checked against
spec §15.1. A task may only start when every task it depends on is `done`.

| Task | Wave | depends_on |
|---|---:|---|
| CS-001 | 0 | — |
| CS-002 | 0 | CS-001 |
| CS-003 | 0 | CS-002 |
| CS-004 | 0 | CS-002 |
| CS-005 | 0 | CS-002 |
| CS-006 | 0 | CS-002 |
| CS-010 | 1 | CS-001, CS-004, CS-005, CS-006 |
| CS-011 | 1 | CS-010 |
| CS-012 | 1 | CS-011 |
| CS-013 | 1 | CS-012 |
| CS-014 | 1 | CS-010 |
| CS-015 | 1 | CS-011 |
| CS-016 | 1 | CS-013, CS-014, CS-015 |
| CS-021 | 2 | CS-011 |
| CS-022 | 2 | CS-011 |
| CS-023 | 2 | CS-021 |
| CS-024 | 2 | CS-012 |
| CS-025 | 2 | CS-013 |
| CS-026 | 2 | CS-010 |
| CS-031 | 3 | CS-015 |
| CS-032 | 3 | CS-015 |
| CS-033 | 3 | CS-024 |
| CS-040 | 4 | CS-003 |
| CS-041 | 4 | CS-040 |
| CS-042 | 4 | CS-040, CS-012 |
| CS-043 | 4 | CS-041 |
| CS-044 | 4 | CS-040 |
| CS-045 | 4 | CS-041, CS-042 |
| CS-050 | 5 | CS-044 |
| CS-051 | 5 | CS-050 |
| CS-060 | 6 | CS-024 |
| CS-061 | 6 | CS-060 |
| CS-062 | 6 | CS-060 |
| CS-070 | 7 | CS-022, CS-026, CS-060 |
| CS-071 | 7 | CS-070 |
| CS-072 | 7 | CS-041 |
| CS-080 | 8 | CS-024 |
| CS-081 | 8 | CS-026, CS-060 |
| CS-082 | 8 | CS-071, CS-072, CS-080, CS-081 |
| CS-090 | 9 | CS-012, CS-024 |
| CS-091 | 9 | CS-031, CS-032, CS-033, CS-082, CS-090 |
| CS-092 | 10 | CS-002 |
| CS-093 | 10 | CS-092 |
| CS-094 | 10 | CS-093, CS-011 |
| CS-095 | 10 | CS-093, CS-011 |
| CS-096 | 10 | CS-093 |
| CS-097 | 10 | CS-090 |

Build order rule (E26): the demo slice CS-010 … CS-016 has priority over every
later wave while it is open and buildable. After that, earliest open task with
met dependencies wins.