# nextRACI — project instructions

nextRACI is an open-source, machine-checkable RACI charter + linter for teams of
humans and AI agents: it declares who is Responsible / Accountable / Consulted /
Informed for each *type* of action — including when an AI agent acts with no human
trigger — and a checker flags the gaps before they bite.

## Language

**This project is English-only.** README, SPEC, CONTRIBUTING, code, comments,
commit messages, issues, and PR descriptions are all in English. (This overrides
any global default-to-Chinese reply rule for repo artifacts; conversation with the
maintainer may still be bilingual.)

## Voice & honesty

- Plain language for a broad audience — engineers *and* governance/compliance
  readers. Prefer "checker" over "linter", "format" over "schema". Gloss RACI on
  first use in standalone docs.
- **Never over-promise.** v0.1 *writes and checks* a charter. It does NOT intercept
  actions or enforce approvals at runtime. The runtime control plane and live
  connectors (HumanLayer/LangGraph) are roadmap, not current claims. Label future
  capability as roadmap. Honest scope boxes beat hype.
- Brand is **nextRACI** (camelCase in prose; `nextraci` as the package/CLI token).

## The four project agents

This repo defines four agents under `.claude/agents/`. Route work to them:

- **writer** — all human-facing prose (README/SPEC/CONTRIBUTING/examples/essays,
  issue & PR text). Edits docs.
- **coder** — Python changes (schema/loader/linter/cli/adapters). Edits code.
- **reviewer** — independent, read-only review before merge/release. Reports only.
- **qa** — runs tests + CLI + packaging smoke, confirms each rule fires. Reports only.

Typical loop for a non-trivial change: **coder** implements → **qa** verifies →
**reviewer** signs off (independent) → **writer** updates docs if behavior changed.
Keep reviewer and qa independent of the change author — do not have the coder
review its own work.

## Checker rules (keep code ⇄ docs in sync)

R1 single accountable · R2 coverage · R3 no contradiction · R4 gate completeness ·
R5 low-risk gating · R6 acyclic authority (**planned, v0.2 stub**). Rule behavior in
`nextraci/linter.py` is the source of truth; README/SPEC must match it. Each active
rule should have a test (one test per rule is the norm).

## Dev quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
nextraci validate examples/sprout/charter.yaml
```
