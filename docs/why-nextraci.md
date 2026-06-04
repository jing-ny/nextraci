# Why nextRACI

*An AI agent on your team just shipped code, sent a message, or spent money — and
no human pressed the button. Who answers for it?*

## The accountability gap

Software teams used to have a comforting property: behind every action was a
person who decided to take it. A deploy happened because an engineer ran it. A
refund went out because someone in support approved it. When something went
wrong, you could ask *who did this?* and get a name.

AI agents quietly removed that property. An agent can now open a pull request,
reply to a customer, reconcile an invoice, or escalate an incident — on its own
schedule, with no human in the loop at the moment it acts. The work still gets
done. But the question *who is accountable for it?* no longer has an automatic
answer, because no human pulled the trigger.

This is the accountability gap, and it is not a hypothetical. The moment you let
an agent act unsupervised — which is the whole point of agents — you have created
an action with a responsible *doer* (the agent) and, very often, no clearly named
*owner*. That gap is invisible right up until the agent does something you have to
answer for.

## Why classic RACI breaks under agentic AI

For decades the standard tool for this was **RACI**: a simple chart naming, for
each kind of work, who is **R**esponsible (does it), **A**ccountable (owns the
outcome — exactly one person), **C**onsulted (gives input), and **I**nformed
(kept in the loop). RACI is good precisely because it forces the uncomfortable
question of single ownership.

But classic RACI carries a buried assumption: **a human starts every task.** The
"Responsible" party is a person who decides to act; the chart describes how
authority flows *around* that human-initiated work. Agentic AI breaks the
assumption in two ways at once:

1. **The doer may not be human.** An agent can be Responsible for an action. RACI
   has no native concept of a non-human actor with real permissions and real
   limits.
2. **There may be no human trigger at all.** The action can originate from the
   agent's own loop. RACI never had to describe "what happens when the thing that
   acts is also the thing that decided to act, and it isn't a person."

The result is that most teams adopting agents either write no RACI at all (and
discover the gap during an incident) or write a slide-deck RACI that no tool can
check and no agent can read. Neither survives contact with a real agent acting at
3 a.m.

## What a charter looks like

nextRACI is one plain-language file — a **charter** — that closes the gap by
answering three *independent* questions for every type of action on the team. The
key insight is that these three questions get mixed up constantly, and separating
them is most of the value:

| Question       | What it asks                     | Example |
|----------------|----------------------------------|---------|
| **Function**   | What do you *do*?                | Orchestrate, Build, Advise, Review, Watch |
| **Permission** | What may you *touch*?            | `edit_code`, `merge`, `deploy`, `spend` — granted or explicitly denied |
| **Authority**  | Whose call *wins* in a conflict? | Expressed via each action's single `accountable` |

The proof these are genuinely independent: a domain expert can be **accountable**
for whether a fact is correct, **denied** any permission to touch the code, yet
able to **block** a merge on correctness grounds — three different axes, none
implying the others.

A charter defines a small set of **roles** once (orchestrator, engineer, expert,
reviewer, monitor), then *assigns* humans and agents to them — adding an agent is
a one-line appointment, not a new rulebook. For each **type of action** (not each
individual task), it names exactly one accountable role, who is consulted, what
permissions the action touches, and — crucially — what happens when the party who
should act is unavailable. Every approval step must declare a timeout behavior and
a `break_glass` emergency path, so the rules can never silently deadlock, and an
agent can never treat "low risk" as a quiet backdoor to act unsupervised.

A built-in checker reads the charter and flags the gaps mechanically: an action
nobody owns, two roles that both think they're in charge, a permission granted but
never used, an approval step that could stall forever. The charter is not a
diagram you draw and forget — it is a file your CI can verify.

## What it is, and what it isn't yet

Honesty is part of the pitch, so the scope box is explicit:

- **Today, nextRACI writes and checks the charter.** You get a clear file format,
  an automatic checker (rules R1–R5), worked examples, and a blank template. That
  is a real, shippable thing: a machine-checkable accountability map for a mixed
  human + agent team.
- **Today, nextRACI does not run your team.** It does not intercept actions or
  enforce approvals at the instant they happen. Tools like LangGraph, CrewAI, and
  HumanLayer already *run* agents and pause them for sign-off. nextRACI sits one
  level up and answers what they don't: *on this specific team, who is allowed to
  do what, and who breaks a tie.*
- **Turning the charter into live, enforced approvals is the roadmap, not a
  claim.** The next milestone is a HumanLayer connector that compiles a charter
  into real gates, plus a team-wide "who outranks whom" map and a check that it
  has no impossible loops. That is stated as a plan, not as something that already
  works.

## How it relates to ISO/IEC 42001 and the EU AI Act

There are two levels at which "who is accountable for the AI" gets asked, and they
are often conflated.

The **governance level** is the boardroom and compliance question: who answers for
the AI system *as a whole*? This is the concern behind standards like **ISO/IEC
42001** (AI management systems) and the **EU AI Act** (risk tiers, obligations on
providers and deployers). These frameworks are essential, but they operate at the
altitude of policies, management systems, and documented responsibility — the
slide deck and the audit trail.

The **operating level** is the missing piece: a precise, machine-checkable charter
for the *day-to-day*, where the AI agents themselves hold real roles, touch real
permissions, and the rules are verified by a tool rather than asserted in a
document. nextRACI lives here. It is the artifact that lets you say to an auditor —
or to yourself, after an incident — "here is the exact file that named who owned
this action, what the agent was and wasn't allowed to do, and what should have
happened when the approver went dark," and then *run the checker to prove the file
is internally consistent.*

Governance frameworks tell you that you must have accountability. nextRACI is one
concrete, verifiable way to actually have it, down to the individual action an
agent takes on its own.

---

*nextRACI is open source (MIT). Start with the
[README](../README.md), the worked example in [`examples/sprout/`](../examples/sprout/),
or the format details in [SPEC.md](../SPEC.md).*
