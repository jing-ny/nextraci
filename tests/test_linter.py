"""Linter tests: for each active rule R1-R5, the Sprout charter passes and one
deliberately broken charter trips exactly that rule. R6 is asserted to be a
stub that always passes.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from nextraci.linter import lint, rule_r6_acyclic_authority
from nextraci.loader import load_charter
from nextraci.schema import Charter

SPROUT = Path(__file__).resolve().parents[1] / "examples" / "sprout" / "charter.yaml"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _base() -> dict:
    """A fresh, minimal charter dict that PASSES R1-R5.

    Each test deep-copies this and mutates one thing to trip a single rule.
    """
    return {
        "project": "test",
        "roles": ["orchestrator", "engineer", "reviewer"],
        "members": [
            {"name": "you", "type": "human", "role": "orchestrator"},
            {"name": "dev", "type": "human", "role": "engineer"},
        ],
        "capabilities": {
            "engineer": {"grant": ["edit_code", "merge"]},
            "reviewer": {"grant": ["block_merge"], "deny": ["edit_code"]},
        },
        "actions": {
            "do_work": {
                "responsible": "engineer",
                "accountable": "engineer",
                "capabilities": ["edit_code"],
            },
            "merge": {
                "responsible": "engineer",
                "accountable": "reviewer",
                "capabilities": ["merge", "block_merge"],
                "gate": {
                    "approver": "reviewer",
                    "on_timeout": "block",
                    "break_glass": {
                        "who": "engineer",
                        "condition": "sev1",
                        "requires_after_review": True,
                    },
                },
            },
        },
    }


def _rules_tripped(data: dict) -> set[str]:
    charter = Charter.model_validate(data)
    return {e.rule for e in lint(charter)}


def test_base_charter_is_clean():
    """Sanity: the minimal base trips no rules."""
    assert _rules_tripped(_base()) == set()


# --------------------------------------------------------------------------- #
# The known-good charter: Sprout passes R1-R5 (R6 is a stub).
# --------------------------------------------------------------------------- #
def test_sprout_passes_all_active_rules():
    charter = load_charter(SPROUT)
    errors = lint(charter)
    assert errors == [], "\n".join(str(e) for e in errors)


# --------------------------------------------------------------------------- #
# R1 — single accountable
# --------------------------------------------------------------------------- #
def test_r1_two_accountable_trips_only_r1():
    data = _base()
    data["actions"]["do_work"]["accountable"] = ["engineer", "reviewer"]
    assert _rules_tripped(data) == {"R1"}


def test_r1_zero_accountable_trips_only_r1():
    data = _base()
    data["actions"]["do_work"]["accountable"] = []
    assert _rules_tripped(data) == {"R1"}


# --------------------------------------------------------------------------- #
# R2 — coverage
# --------------------------------------------------------------------------- #
def test_r2_undeclared_capability_trips_only_r2():
    data = _base()
    data["actions"]["do_work"]["capabilities"] = ["edit_code", "deploy"]  # deploy undeclared
    assert _rules_tripped(data) == {"R2"}


def test_r2_dead_capability_trips_only_r2():
    data = _base()
    data["capabilities"]["engineer"]["grant"].append("deploy")  # declared, never used
    assert _rules_tripped(data) == {"R2"}


# --------------------------------------------------------------------------- #
# R3 — no contradiction
# --------------------------------------------------------------------------- #
def test_r3_grant_and_deny_same_capability_trips_only_r3():
    data = _base()
    data["capabilities"]["engineer"]["deny"] = ["edit_code"]  # also granted
    assert _rules_tripped(data) == {"R3"}


# --------------------------------------------------------------------------- #
# R4 — gate completeness
# --------------------------------------------------------------------------- #
def test_r4_missing_break_glass_trips_only_r4():
    data = _base()
    del data["actions"]["merge"]["gate"]["break_glass"]
    assert _rules_tripped(data) == {"R4"}


def test_r4_consulted_but_denied_without_route_trips_only_r4():
    data = _base()
    # reviewer is denied edit_code but consulted on an action that touches it,
    # with no suggestion_route -> its input would be silently dropped.
    data["actions"]["do_work"]["consulted"] = ["reviewer"]
    assert _rules_tripped(data) == {"R4"}


def test_r4_suggestion_route_satisfies_the_rule():
    data = _base()
    data["actions"]["do_work"]["consulted"] = ["reviewer"]
    data["actions"]["do_work"]["suggestion_route"] = {
        "from": "reviewer",
        "to": "engineer",
        "as": "objection",
    }
    assert _rules_tripped(data) == set()


# --------------------------------------------------------------------------- #
# R5 — low-risk gating
# --------------------------------------------------------------------------- #
def test_r5_proceed_if_low_risk_without_flag_trips_only_r5():
    data = _base()
    data["actions"]["merge"]["gate"]["on_timeout"] = "proceed_if_low_risk"
    # merge is NOT low_risk -> illegal
    assert _rules_tripped(data) == {"R5"}


def test_r5_proceed_if_low_risk_with_flag_is_allowed():
    data = _base()
    data["actions"]["merge"]["gate"]["on_timeout"] = "proceed_if_low_risk"
    data["actions"]["merge"]["low_risk"] = True
    assert _rules_tripped(data) == set()


# --------------------------------------------------------------------------- #
# R6 — acyclic authority (STUB)
# --------------------------------------------------------------------------- #
def test_r6_is_a_stub_that_always_passes():
    # Stub returns no errors regardless of input, for both base and Sprout.
    assert rule_r6_acyclic_authority(Charter.model_validate(_base())) == []
    assert rule_r6_acyclic_authority(load_charter(SPROUT)) == []


# --------------------------------------------------------------------------- #
# schema-level referential integrity (distinct from linter rules)
# --------------------------------------------------------------------------- #
def test_undeclared_role_reference_is_a_schema_error():
    data = _base()
    data["actions"]["do_work"]["accountable"] = "ghost"  # not a declared role
    with pytest.raises(Exception):
        Charter.model_validate(data)
