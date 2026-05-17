"""
The Orchestrator — Fully agnostic. All config injected from the target repo.

Manages the full pipeline:
PRD → Project Manager → Tech Lead → Developer → Tester → Release Engineer → PR
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from github import Github, GithubException
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import PluginConfig
from core.agents import (
    PROJECT_MANAGER,
    TECH_LEAD,
    DEVELOPER,
    TESTER,
    RELEASE_ENGINEER,
)
from core.llm_client import get_llm_client
from core.ralph_loop import RalphLoop

console = Console()


class Orchestrator:
    """
    The main pipeline controller.
    Config is INJECTED from the target repo — the orchestrator is fully agnostic.
    """

    def __init__(self, prd_path: str, config: PluginConfig):
        self.prd_path = prd_path
        self.config = config
        self.repo_path = config.repo_path
        self.agent_context = config.agent_context
        self.prd_content = self._load_prd()
        self.tickets: list[dict] = []
        self.completed_tickets: list[dict] = []

    # ── Phase 0: Load Inputs ──────────────────

    def _load_prd(self) -> str:
        """Load the PRD/SRD document."""
        path = Path(self.prd_path)
        if not path.exists():
            raise FileNotFoundError(f"PRD file not found: {self.prd_path}")

        if path.suffix == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)
                return text
            except ImportError:
                raise ImportError("pdfplumber is required for PDF files. Run: pip install pdfplumber")
        else:
            return path.read_text(encoding="utf-8")

    # ── Phase 1: Project Manager ──────────────

    def run_project_manager(self) -> list[dict]:
        """Run the PM agent to break the PRD into tickets."""
        console.print(Panel("[bold]📋 Phase 1: Project Manager — Breaking PRD into tickets[/bold]", style="magenta"))

        pm_model = self.config.models.get("project_manager")
        os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
        client = get_llm_client(pm_model.provider if pm_model else "openai")

        prompt = (
            f"## PRD Document\n\n{self.prd_content}\n\n"
            f"## Repository Context\n\n{self.agent_context}\n\n"
            f"Break this PRD into implementable GitHub Issues."
        )

        response = client.chat.completions.create(
            model=pm_model.model if pm_model else "gpt-4o",
            messages=[
                {"role": "system", "content": PROJECT_MANAGER.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=pm_model.temperature if pm_model else 0.3,
            max_tokens=pm_model.max_tokens if pm_model else 4096,
            response_format={"type": "json_object"},
        )

        raw_output = response.choices[0].message.content
        try:
            parsed = json.loads(raw_output)
            if isinstance(parsed, list):
                self.tickets = parsed
            elif isinstance(parsed, dict) and "tickets" in parsed:
                self.tickets = parsed["tickets"]
            else:
                self.tickets = [parsed]
        except json.JSONDecodeError:
            console.print(f"[red]ERROR: PM returned invalid JSON.[/red]")
            console.print(raw_output)
            return []

        self._display_tickets()
        return self.tickets

    def _display_tickets(self):
        """Pretty-print the generated tickets."""
        table = Table(title="📋 Generated Tickets", show_lines=True)
        table.add_column("#", style="bold", width=4)
        table.add_column("Title", style="cyan", min_width=40)
        table.add_column("Labels", style="green")
        table.add_column("Priority", style="yellow", width=8)

        for i, ticket in enumerate(self.tickets, 1):
            table.add_row(
                str(i),
                ticket.get("title", "Untitled"),
                ", ".join(ticket.get("labels", [])),
                str(ticket.get("priority", "N/A")),
            )
        console.print(table)

    # ── Phase 1b: Create GitHub Issues ────────

    def create_github_issues(self) -> list[dict]:
        """Push the tickets to GitHub as Issues."""
        console.print(Panel("[bold]🐙 Creating GitHub Issues[/bold]", style="blue"))

        try:
            gh = Github(self.config.github_token)
            repo = gh.get_repo(self.config.github_repo)
        except Exception as e:
            console.print(f"[red]ERROR connecting to GitHub: {e}[/red]")
            return self.tickets

        for ticket in self.tickets:
            try:
                body = (
                    f"{ticket.get('description', '')}\n\n"
                    f"### Acceptance Criteria\n"
                    + "\n".join(f"- [ ] {ac}" for ac in ticket.get("acceptance_criteria", []))
                )
                issue = repo.create_issue(
                    title=ticket["title"],
                    body=body,
                    labels=ticket.get("labels", []),
                )
                ticket["github_issue_number"] = issue.number
                ticket["github_issue_url"] = issue.html_url
                console.print(f"  ✅ Created Issue #{issue.number}: {ticket['title']}")
            except GithubException as e:
                console.print(f"  ❌ Failed to create issue: {e.data.get('message', str(e))}")

        return self.tickets

    # ── Phase 2: Tech Lead ────────────────────

    def run_tech_lead(self, ticket: dict) -> dict:
        """Run the Tech Lead agent to enrich a ticket."""
        console.print(Panel(
            f"[bold]👨‍💼 Phase 2: Tech Lead — Analyzing: {ticket['title']}[/bold]",
            style="magenta",
        ))

        task_prompt = (
            f"## Ticket\n"
            f"Title: {ticket['title']}\n"
            f"Description: {ticket.get('description', 'N/A')}\n"
            f"Acceptance Criteria:\n"
            + "\n".join(f"- {ac}" for ac in ticket.get("acceptance_criteria", []))
            + "\n\nExplore the codebase and provide implementation guidance."
        )

        loop = RalphLoop(
            agent=TECH_LEAD, repo_path=self.repo_path,
            config=self.config, context=self.agent_context,
        )
        result = loop.run(task_prompt)

        try:
            enrichment = json.loads(result)
            ticket["implementation_plan"] = enrichment.get("implementation_plan", [])
            ticket["files_to_modify"] = enrichment.get("files_to_modify", [])
            ticket["files_to_create"] = enrichment.get("files_to_create", [])
            ticket["build_command"] = enrichment.get("build_command", "")
            ticket["test_command"] = enrichment.get("test_command", "")
        except (json.JSONDecodeError, TypeError):
            ticket["implementation_plan"] = [result]

        return ticket

    # ── Phase 3: Developer (Ralph Loop) ───────

    def run_developer(self, ticket: dict) -> str:
        """Run the Developer agent in a Ralph Loop."""
        console.print(Panel(
            f"[bold]💻 Phase 3: Developer — Coding: {ticket['title']}[/bold]",
            style="green",
        ))

        task_prompt = (
            f"## Ticket\n"
            f"Title: {ticket['title']}\n"
            f"Description: {ticket.get('description', '')}\n\n"
            f"## Implementation Plan (from Tech Lead)\n"
            + "\n".join(f"- {step}" for step in ticket.get("implementation_plan", ["No plan provided."]))
            + f"\n\n## Build Command\n{ticket.get('build_command', 'Detect from project files.')}"
        )

        loop = RalphLoop(
            agent=DEVELOPER, repo_path=self.repo_path,
            config=self.config, context=self.agent_context,
        )
        return loop.run(task_prompt)

    # ── Phase 4: Tester (Ralph Loop) ──────────

    def run_tester(self, ticket: dict) -> str:
        """Run the Tester agent to write and run tests."""
        console.print(Panel(
            f"[bold]🧪 Phase 4: Tester — Validating: {ticket['title']}[/bold]",
            style="blue",
        ))

        task_prompt = (
            f"## Ticket\n"
            f"Title: {ticket['title']}\n"
            f"Acceptance Criteria:\n"
            + "\n".join(f"- {ac}" for ac in ticket.get("acceptance_criteria", []))
            + f"\n\n## Test Command\n{ticket.get('test_command', 'Detect from project files.')}"
            + f"\n\nFiles that were created/modified:\n"
            + "\n".join(f"- {f}" for f in ticket.get("files_to_create", []) + ticket.get("files_to_modify", []))
        )

        loop = RalphLoop(
            agent=TESTER, repo_path=self.repo_path,
            config=self.config, context=self.agent_context,
        )
        return loop.run(task_prompt)

    # ── Phase 5: Release Engineer ─────────────

    def run_release_engineer(self, branch_name: str) -> str:
        """Run the Release Engineer to commit, push, and create a PR."""
        console.print(Panel("[bold]🚀 Phase 5: Release Engineer — Shipping[/bold]", style="red"))

        tickets_summary = "\n".join(
            f"- Closes #{t.get('github_issue_number', '?')}: {t['title']}"
            for t in self.completed_tickets
        )

        task_prompt = (
            f"## Completed Tickets\n{tickets_summary}\n\n"
            f"## Branch Name\n{branch_name}\n\n"
            f"Commit all changes, push the branch, and create a Pull Request."
        )

        loop = RalphLoop(
            agent=RELEASE_ENGINEER, repo_path=self.repo_path,
            config=self.config, context=self.agent_context,
        )
        return loop.run(task_prompt)

    # ── Full Pipeline ─────────────────────────

    def run_full_pipeline(self):
        """Execute the entire pipeline from PRD to PR."""
        console.print(Panel(
            "[bold]🏁 STARTING FULL PIPELINE[/bold]\n"
            f"PRD: {self.prd_path}\n"
            f"Repo: {self.repo_path}",
            style="bold white on blue",
        ))

        # Phase 1: Project Manager creates tickets
        tickets = self.run_project_manager()
        if not tickets:
            console.print("[red]No tickets generated. Aborting.[/red]")
            return

        # Phase 1b: Push tickets to GitHub
        self.create_github_issues()

        # Branch name
        branch_name = "feat/agentic-" + tickets[0]["title"].split("]")[-1].strip().lower().replace(" ", "-")[:30]

        # Process each ticket
        for i, ticket in enumerate(tickets, 1):
            console.print(f"\n{'='*60}")
            console.print(f"[bold]Processing Ticket {i}/{len(tickets)}: {ticket['title']}[/bold]")
            console.print(f"{'='*60}")

            # Phase 2: Tech Lead enriches the ticket
            ticket = self.run_tech_lead(ticket)

            # Phase 3 & 4: Developer ↔ Tester feedback loop
            for cycle in range(self.config.max_dev_tester_cycles):
                console.print(f"\n[bold]── Dev/Test Cycle {cycle + 1} ──[/bold]")

                dev_result = self.run_developer(ticket)
                if "BUILD_FAILED" in dev_result:
                    console.print(f"[red]Developer could not complete the build. Skipping ticket.[/red]")
                    break

                test_result = self.run_tester(ticket)
                if "TESTS_PASSED" in test_result:
                    console.print(f"[green]✅ Ticket complete: {ticket['title']}[/green]")
                    self.completed_tickets.append(ticket)
                    break
                elif "CODE_BUG" in test_result:
                    console.print(f"[yellow]🐛 Bug found. Sending back to Developer...[/yellow]")
                    ticket["bug_report"] = test_result
                else:
                    console.print(f"[yellow]Unexpected tester output. Moving on.[/yellow]")
                    self.completed_tickets.append(ticket)
                    break

        # Phase 5: Release Engineer
        if self.completed_tickets:
            self.run_release_engineer(branch_name)
        else:
            console.print("[red]No tickets were completed. No PR to create.[/red]")

        console.print(Panel("[bold green]🏁 PIPELINE COMPLETE[/bold green]", style="green"))

    # ── Direct Pipeline (Doc → Code → PR) ─────

    def run_direct_pipeline(self):
        """
        Execute the DIRECT pipeline: Dev Doc → Tech Lead → Developer → Tester → PR.

        Use this when the document is already a fully-cooked dev spec
        (not a high-level PRD that needs to be broken into tickets).
        The entire doc is treated as a single implementation task.
        """
        console.print(Panel(
            "[bold]🏁 STARTING DIRECT PIPELINE[/bold]\n"
            f"Doc: {self.prd_path}\n"
            f"Repo: {self.repo_path}\n\n"
            "[dim]Mode: Direct (Doc → Code → Tests → PR) — skipping ticket creation[/dim]",
            style="bold white on magenta",
        ))

        # Create a synthetic "ticket" from the entire dev doc
        doc_title = Path(self.prd_path).stem.replace("-", " ").replace("_", " ").title()
        ticket = {
            "title": f"[Direct] {doc_title}",
            "description": self.prd_content,
            "acceptance_criteria": [],  # Tech Lead will extract these from the doc
            "labels": ["direct-mode"],
        }

        # Branch name
        branch_name = "feat/agentic-" + doc_title.lower().replace(" ", "-")[:30]

        console.print(f"\n{'='*60}")
        console.print(f"[bold]📄 Processing: {doc_title}[/bold]")
        console.print(f"{'='*60}")

        # Phase 1 (Tech Lead): Analyze the dev doc and create an implementation plan
        console.print(Panel(
            f"[bold]👨‍💼 Tech Lead — Analyzing dev doc and creating implementation plan[/bold]",
            style="magenta",
        ))

        task_prompt = (
            f"## Development Document\n"
            f"The following is a COMPLETE development specification document. "
            f"It is NOT a high-level PRD — it contains detailed implementation instructions.\n\n"
            f"{self.prd_content}\n\n"
            f"Analyze this document and the existing codebase. "
            f"Create a detailed implementation plan with specific file paths."
        )

        loop = RalphLoop(
            agent=TECH_LEAD, repo_path=self.repo_path,
            config=self.config, context=self.agent_context,
        )
        result = loop.run(task_prompt)

        try:
            enrichment = json.loads(result)
            ticket["implementation_plan"] = enrichment.get("implementation_plan", [])
            ticket["files_to_modify"] = enrichment.get("files_to_modify", [])
            ticket["files_to_create"] = enrichment.get("files_to_create", [])
            ticket["build_command"] = enrichment.get("build_command", "")
            ticket["test_command"] = enrichment.get("test_command", "")
        except (json.JSONDecodeError, TypeError):
            ticket["implementation_plan"] = [result]

        # Phase 2 & 3 (Developer ↔ Tester feedback loop)
        for cycle in range(self.config.max_dev_tester_cycles):
            console.print(f"\n[bold]── Dev/Test Cycle {cycle + 1} ──[/bold]")

            dev_result = self.run_developer(ticket)
            if "BUILD_FAILED" in dev_result:
                console.print(f"[red]Developer could not complete the build. Aborting.[/red]")
                return

            test_result = self.run_tester(ticket)
            if "TESTS_PASSED" in test_result:
                console.print(f"[green]✅ Implementation complete and tests passing![/green]")
                self.completed_tickets.append(ticket)
                break
            elif "CODE_BUG" in test_result:
                console.print(f"[yellow]🐛 Bug found. Sending back to Developer...[/yellow]")
                ticket["bug_report"] = test_result
            else:
                console.print(f"[yellow]Unexpected tester output. Moving on.[/yellow]")
                self.completed_tickets.append(ticket)
                break

        # Phase 4 (Release Engineer): Ship it
        if self.completed_tickets:
            self.run_release_engineer(branch_name)
        else:
            console.print("[red]Implementation failed. No PR to create.[/red]")

        console.print(Panel("[bold green]🏁 DIRECT PIPELINE COMPLETE[/bold green]", style="green"))
