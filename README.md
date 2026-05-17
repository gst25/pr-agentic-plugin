# Agentic Plugin 🤖

> Turn PRDs into Pull Requests — powered by AI agents.

A local CLI plugin that reads your Product Requirements Documents (PRD/SRD) and autonomously creates GitHub tickets, writes code, runs tests, and raises a Pull Request — all using a team of AI agents.

## 🏗️ Architecture

The plugin orchestrates **5 AI agents**, each mirroring a real engineering role:

| Agent | Role | What it does |
|---|---|---|
| 🧠 **Project Manager** | Planner | Reads the PRD and breaks it into structured GitHub tickets |
| 👨‍💼 **Tech Lead** | Architect | Scans the repo and enriches tickets with file-level guidance |
| 💻 **Developer** | Coder | Writes production code inside a Ralph Loop until it compiles |
| 🧪 **Tester** | QA | Writes tests and validates code against acceptance criteria |
| 🚀 **Release Engineer** | Shipper | Commits, pushes, and raises the final Pull Request |

## 🚀 Quick Start

### 1. Install the plugin
```bash
git clone https://github.com/YOUR_USERNAME/agentic-plugin.git
cd agentic-plugin
pip install -e .
```

### 2. Initialize in any repo
```bash
cd ~/projects/your-java-project
agentic init
```

This creates a `.agentic/` config directory in your repo:
```
your-repo/
├── .agentic/
│   ├── config.yaml          ← Your API keys + GitHub settings
│   ├── models.yaml          ← Which LLM each agent uses
│   └── AGENT_CONTEXT.md     ← Your repo's coding rules & standards
```

### 3. Configure
Fill in `.agentic/config.yaml` with your API keys and `.agentic/AGENT_CONTEXT.md` with your repo's build commands, folder structure, and coding standards.

### 4. Run
```bash
# Full pipeline: PRD → Tickets → Code → Tests → PR
agentic run --prd docs/feature-prd.md

# Direct pipeline: Dev Doc → Code → Tests → PR (skip ticket creation)
agentic run --prd docs/dev-spec.md --mode direct
```

## 🔀 Pipeline Modes

| Mode | Flow | Use When |
|---|---|---|
| `full` (default) | PRD → PM → Tickets → Tech Lead → Developer → Tester → PR | You have a high-level PRD that needs to be broken into tasks |
| `direct` | Doc → Tech Lead → Developer → Tester → PR | You have a detailed dev doc ready to be implemented directly |

## 🛠️ Tech Stack

- **Python 3.10+** — Core language
- **OpenAI / Anthropic / Google / Ollama** — LLM providers (configurable per agent)
- **PyGithub** — GitHub API integration
- **GitPython** — Local git operations
- **Rich** — Beautiful CLI output

## 📁 Project Structure

```
agentic-plugin/
├── main.py                         # CLI entry point (agentic init / run)
├── config.py                       # Resolves config from target repo's .agentic/
├── setup.py                        # pip installable
├── core/
│   ├── agents/                     # One file per agent
│   │   ├── project_manager.py
│   │   ├── tech_lead.py
│   │   ├── developer.py
│   │   ├── tester.py
│   │   └── release_engineer.py
│   ├── base_agent.py               # Shared AgentDefinition dataclass
│   ├── llm_client.py               # Multi-provider LLM factory
│   ├── orchestrator.py             # Pipeline controller
│   ├── ralph_loop.py               # The Ralph Loop execution engine
│   └── init_command.py             # 'agentic init' scaffolding
├── tools/                          # One file per tool
│   ├── list_directory.py
│   ├── read_file.py
│   ├── write_file.py
│   ├── run_command.py
│   ├── git_branch.py
│   ├── git_commit.py
│   ├── git_push.py
│   └── git_pr.py
├── docs/
│   └── ROADMAP_FLOWS.md            # Future pipeline flows roadmap
└── samples/
    ├── sample-prd.md               # Example PRD document
    └── AGENT_CONTEXT.md            # Example repo context file
```

## 🔑 Key Concepts

### Ralph Loop
Instead of running the agent in one long session, the Ralph Loop spawns a **fresh LLM call per iteration**. State is stored externally (in files and git), preventing context window bloat and hallucination drift.

### AGENT_CONTEXT.md
A Markdown file in your repo that teaches the AI agents your coding standards, build commands, folder structure, and rules. Think of it as onboarding documentation for your AI teammates.

### Per-Agent Model Config
Each agent can use a different LLM. Use Claude for the Developer (best at coding), GPT-4o-mini for the Release Engineer (cheap, simple task), and a local Ollama model for the Tester.

## 📄 License
MIT
