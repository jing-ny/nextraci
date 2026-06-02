"""The nextRACI linter: rules R1-R5 active, R6 stubbed for v0.1.

Each rule is a pure function ``rule(charter) -> list[LintError]``. ``lint()``
runs them all and returns every error found. Errors are structured and name the
offending action/role so ``nextraci validate`` can print an actionable report.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schema import ANY, Charter

# Ordered registry of (rule id, human title, function). Populated at the bottom
# of this module once the rule functions are defined.
RULES: list[tuple[str, str, "RuleFn"]] = []


@dataclass(frozen=True)
class LintError:
    """A single linter finding."""

    rule: str          # e.g. "R1"
    target: str        # the offending action/role/capability
    message: str

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"[{self.rule}] {self.target}: {self.message}"


RuleFn = "callable"  # see RULES typing note above


# --------------------------------------------------------------------------- #
# R1 - single accountable
# --------------------------------------------------------------------------- #
def rule_r1_single_accountable(charter: Charter) -> list[LintError]:
    """Every action type has exactly one accountable role.

    0 accountable -> a gap (work nobody claims).
    2+ accountable -> a conflict (two roles each think they own it).
    """
    errors: list[LintError] = []
    for name, action in charter.actions.items():
        n = len(action.accountable)
        if n == 0:
            errors.append(
                LintError("R1", name, "has no accountable role (gap: nobody owns this).")
            )
        elif n > 1:
            joined = ", ".join(action.accountable)
            errors.append(
                LintError(
                    "R1",
                    name,
                    f"has {n} accountable roles ({joined}) — exactly one is required "
                    "(conflict: two roles each think they own it).",
                )
            )
    return errors


# --------------------------------------------------------------------------- #
# R2 - coverage
# --------------------------------------------------------------------------- #
def rule_r2_coverage(charter: Charter) -> list[LintError]:
    """No dead permissions, and no action touching an undeclared capability."""
    errors: list[LintError] = []
    declared = charter.declared_capabilities()

    used: set[str] = set()
    for name, action in charter.actions.items():
        for cap in action.capabilities:
            used.add(cap)
            if cap not in declared:
                errors.append(
                    LintError(
                        "R2",
                        name,
                        f"touches capability {cap!r} which is not declared in any "
                        "role's grant/deny.",
                    )
                )

    for cap in sorted(declared - used):
        errors.append(
            LintError(
                "R2",
                cap,
                "capability is declared but no action touches it (dead permission).",
            )
        )
    return errors


# --------------------------------------------------------------------------- #
# R3 - no contradiction
# --------------------------------------------------------------------------- #
def rule_r3_no_contradiction(charter: Charter) -> list[LintError]:
    """No role both grants and denies the same capability."""
    errors: list[LintError] = []
    for role in charter.get_roles():
        clash = set(role.capabilities.grant) & set(role.capabilities.deny)
        for cap in sorted(clash):
            errors.append(
                LintError(
                    "R3",
                    role.name,
                    f"both grants and denies capability {cap!r}.",
                )
            )
    return errors


# --------------------------------------------------------------------------- #
# R4 - gate completeness
# --------------------------------------------------------------------------- #
def rule_r4_gate_completeness(charter: Charter) -> list[LintError]:
    """Every gate declares on_timeout AND break_glass; every deny that blocks a
    downstream action declares a suggestion_route.

    A consulted role is "blocked but consulted" when it is denied a capability
    that the action touches: its input matters but it cannot act, so the charter
    must declare where its suggestion goes (a suggestion_route ``from`` it).
    """
    errors: list[LintError] = []
    deny_by_role = {r.name: set(r.capabilities.deny) for r in charter.get_roles()}

    for name, action in charter.actions.items():
        if action.gate is not None:
            # on_timeout is required by the schema, so we only check break_glass.
            if action.gate.break_glass is None:
                errors.append(
                    LintError("R4", name, "gate does not declare a break_glass path.")
                )

        touched = set(action.capabilities)
        for role in action.consulted:
            blocked = deny_by_role.get(role, set()) & touched
            if not blocked:
                continue
            route = action.suggestion_route
            if route is None or route.from_ != role:
                caps = ", ".join(sorted(blocked))
                errors.append(
                    LintError(
                        "R4",
                        name,
                        f"role {role!r} is consulted but denied capability(ies) "
                        f"[{caps}] this action touches; declare a suggestion_route "
                        f"from {role!r} so its input is not silently dropped.",
                    )
                )
    return errors


# --------------------------------------------------------------------------- #
# R5 - low-risk gating
# --------------------------------------------------------------------------- #
def rule_r5_low_risk_gating(charter: Charter) -> list[LintError]:
    """``on_timeout: proceed_if_low_risk`` is legal only on a ``low_risk`` action.

    This closes the "low risk = silent backdoor" loophole: an agent can never be
    allowed to act on timeout unless the action is explicitly tagged low_risk.
    """
    errors: list[LintError] = []
    for name, action in charter.actions.items():
        if action.gate is None:
            continue
        if action.gate.is_proceed_if_low_risk and not action.low_risk:
            errors.append(
                LintError(
                    "R5",
                    name,
                    "uses on_timeout: proceed_if_low_risk but is not tagged "
                    "low_risk: true (proceed_if_low_risk is a guarded opt-in).",
                )
            )
    return errors


# --------------------------------------------------------------------------- #
# R6 - acyclic authority (STUB for v0.1)
# --------------------------------------------------------------------------- #
def rule_r6_acyclic_authority(charter: Charter) -> list[LintError]:
    """STUB. Always passes in v0.1.

    R6 will assert that the global veto/escalation graph has no cycles (no
    infinite tie-break loops). In v0.1 authority is expressed *only* via each
    action's ``accountable`` field — there is no separate global authority graph
    to check yet, so this rule is intentionally a no-op.

    TODO(v0.2): once a global veto/escalation graph exists, build the directed
    graph and detect cycles here.
    """
    _ = charter  # unused until v0.2
    return []


RULES = [
    ("R1", "single accountable", rule_r1_single_accountable),
    ("R2", "coverage", rule_r2_coverage),
    ("R3", "no contradiction", rule_r3_no_contradiction),
    ("R4", "gate completeness", rule_r4_gate_completeness),
    ("R5", "low-risk gating", rule_r5_low_risk_gating),
    ("R6", "acyclic authority (stub)", rule_r6_acyclic_authority),
]


def lint(charter: Charter) -> list[LintError]:
    """Run every rule and return all findings, in rule order."""
    errors: list[LintError] = []
    for _id, _title, fn in RULES:
        errors.extend(fn(charter))
    return errors
