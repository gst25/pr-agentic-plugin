# 🔀 Additional Pipeline Flows — Analysis

We currently have two flows:
- **`full`**: PRD → Tickets → Code → Tests → PR
- **`direct`**: Dev Doc → Code → Tests → PR

Below are additional flows that map to real-world engineering scenarios. Each one is ranked by **impact** (how useful it is) and **complexity** (how hard it is to build).

---

## ✅ Recommended Flows

### Flow 3: `bugfix` — Bug Report → Fix → PR
**Trigger:** A bug report (GitHub Issue, Jira ticket, or a text description).
**Use Case:** Someone reports *"Users get a 500 error when resetting password with an expired token."* The plugin reads the bug, finds the relevant code, fixes it, writes a regression test, and raises a PR.

```
🐛 Bug Report → 👨‍💼 Tech Lead (locates the bug) → 💻 Developer (fixes it) → 🧪 Tester (regression test) → 🚀 PR
```

| Attribute | Details |
|---|---|
| **Impact** | 🔥 Very High — bugs are the #1 daily interruption for developers |
| **Complexity** | Medium — the hard part is the Tech Lead accurately locating the buggy code |
| **CLI** | `agentic run --issue 42` or `agentic run --bug "500 error on /reset-password"` |

---

### Flow 4: `refactor` — Refactoring Instructions → PR
**Trigger:** A refactoring request like *"Migrate all controllers from field injection to constructor injection"* or *"Split UserService into UserQueryService and UserCommandService"*.
**Use Case:** Tech debt cleanup. The agent scans all affected files, applies the refactoring pattern consistently, ensures nothing breaks, and raises a PR.

```
🔧 Refactor Request → 👨‍💼 Tech Lead (finds all affected files) → 💻 Developer (applies changes) → 🧪 Tester (ensures no regressions) → 🚀 PR
```

| Attribute | Details |
|---|---|
| **Impact** | 🔥 High — refactoring is tedious and error-prone, perfect for AI |
| **Complexity** | Medium — needs the Tech Lead to find ALL affected files, not just one |
| **CLI** | `agentic run --refactor "Migrate from @Autowired to constructor injection"` |

---

### Flow 5: `test` — Add Tests for Existing Code → PR
**Trigger:** A request to improve test coverage for specific modules that already exist but lack tests.
**Use Case:** *"We need to add unit tests for UserService, AuthService, and PasswordResetService — they currently have 0% coverage."*

```
📋 Test Request → 👨‍💼 Tech Lead (reads existing code) → 🧪 Tester (writes tests) → 🚀 PR
```

| Attribute | Details |
|---|---|
| **Impact** | 🔥 High — most teams have a test coverage gap they never get around to fixing |
| **Complexity** | Low — no code changes, just reading existing code and writing tests |
| **CLI** | `agentic run --test "Add unit tests for src/services/"` |

---

### Flow 6: `review` — Code Review Agent (No PR, Just Feedback)
**Trigger:** A developer pushes a branch and wants AI feedback before asking a human reviewer.
**Use Case:** *"I just finished this feature branch. Review it for bugs, security issues, and code quality."* The agent reads the diff, and outputs a structured review (not a PR, just comments).

```
🔍 Branch/PR → 👨‍💼 Tech Lead (reviews architecture) → 🧪 Tester (checks for edge cases) → 📝 Review Report
```

| Attribute | Details |
|---|---|
| **Impact** | High — catches issues before human review, saves reviewer time |
| **Complexity** | Low — read-only, no file writes, just analysis and a report |
| **CLI** | `agentic review --branch feat/forgot-password` |

---

### Flow 7: `docs` — Generate/Update Documentation → PR
**Trigger:** A request to generate or update documentation for existing code (API docs, README, Javadoc, inline comments).
**Use Case:** *"Generate OpenAPI/Swagger documentation for all REST endpoints"* or *"Add Javadoc to all public methods in the services/ folder."*

```
📝 Doc Request → 👨‍💼 Tech Lead (scans codebase) → 💻 Developer (writes docs/comments) → 🚀 PR
```

| Attribute | Details |
|---|---|
| **Impact** | Medium-High — documentation is universally neglected |
| **Complexity** | Low — reading code and writing markdown/comments is easy for LLMs |
| **CLI** | `agentic run --docs "Generate API docs for all controllers"` |

---

## 🟡 Nice-to-Have Flows (Future)

### Flow 8: `migrate` — Framework/Library Migration
**Use Case:** *"Migrate from JUnit 4 to JUnit 5"* or *"Upgrade Spring Boot from 2.x to 3.x"*.
**Why future:** Migrations are complex and often involve subtle breaking changes. Needs very careful testing.

### Flow 9: `security` — Security Audit
**Use Case:** *"Scan the codebase for SQL injection, XSS, hardcoded secrets, and insecure dependencies."*
**Why future:** Needs integration with security scanning tools (e.g., Semgrep, Snyk).

### Flow 10: `onboard` — Generate AGENT_CONTEXT.md Automatically
**Use Case:** For new repos that don't have an `AGENT_CONTEXT.md` yet. The agent scans the entire repo and auto-generates the context file.
**Why useful:** Removes the manual step of writing the context file.

```
📁 Repo → 🧠 Analyzer (scans structure, package.json, pom.xml, etc.) → 📄 .agentic/AGENT_CONTEXT.md
```

---

## 📊 Priority Matrix

| Flow | Impact | Complexity | Recommendation |
|---|---|---|---|
| `bugfix` | 🔥🔥🔥 | Medium | **Build next** |
| `refactor` | 🔥🔥🔥 | Medium | **Build next** |
| `test` | 🔥🔥🔥 | Low | **Build next** (easiest win) |
| `review` | 🔥🔥 | Low | Build soon |
| `docs` | 🔥🔥 | Low | Build soon |
| `onboard` | 🔥🔥 | Low | Build soon |
| `migrate` | 🔥🔥 | High | Future |
| `security` | 🔥🔥 | High | Future |

---

## ❓ Which flows would you like to implement next?

My recommendation: Start with **`bugfix`**, **`test`**, and **`refactor`** — they cover the most common daily developer pain points and reuse the agents we've already built.
