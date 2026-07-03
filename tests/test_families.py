"""Tests for the five signal families, the MockProvider, and the Runner."""

import pytest

from signalbench import MockProvider, Runner, all_families
from signalbench.core import Legitimacy, VerdictLabel
from signalbench.families import FAMILIES, get_family

FAMILY_NAMES = list(FAMILIES.keys())


def test_registry_has_five_families():
    assert set(FAMILY_NAMES) == {
        "time",
        "access_deny",
        "memory_label",
        "injection",
        "bot_policy",
    }
    assert len(all_families()) == 5


@pytest.mark.parametrize("name", FAMILY_NAMES)
def test_family_builds_items_with_strata(name):
    fam = get_family(name)
    items = fam.build_items()
    assert items, f"{name} built no items"
    legs = {it.legitimacy for it in items}
    # Every family ships a NONE calibration probe.
    assert Legitimacy.NONE in legs
    # Every family has at least one scored (legit or illegit) item.
    assert legs & {Legitimacy.LEGITIMATE, Legitimacy.ILLEGITIMATE}
    # Every illegitimate item defines forbidden_tokens (needed for grading).
    for it in items:
        if it.legitimacy == Legitimacy.ILLEGITIMATE:
            assert it.expected.get("forbidden_tokens"), it.item_id


def test_time_family_has_both_quadrants():
    fam = get_family("time")
    legs = {it.legitimacy for it in fam.build_items()}
    assert Legitimacy.LEGITIMATE in legs  # uptake / under-compliance pole
    assert Legitimacy.ILLEGITIMATE in legs  # fake-now / over-compliance pole


def test_access_deny_has_conditional_flip():
    fam = get_family("access_deny")
    ids = [it.item_id for it in fam.build_items()]
    assert any("flip" in i for i in ids)


@pytest.mark.parametrize("name", FAMILY_NAMES)
def test_oracle_grades_all_correct(name):
    fam = get_family(name)
    provider = MockProvider(policy="oracle")
    for it in fam.build_items():
        resp = provider.complete(it)
        v = fam.grade(it, resp)
        assert v.label == VerdictLabel.CORRECT, (name, it.item_id, v.rationale)
        assert v.score == 1.0


@pytest.mark.parametrize("name", FAMILY_NAMES)
def test_always_comply_over_complies_on_illegit(name):
    fam = get_family(name)
    provider = MockProvider(policy="always_comply")
    for it in fam.build_items():
        v = fam.grade(it, provider.complete(it))
        if it.legitimacy == Legitimacy.ILLEGITIMATE:
            assert v.label == VerdictLabel.OVER_COMPLIANCE, (name, it.item_id)
        elif it.legitimacy == Legitimacy.LEGITIMATE:
            assert v.label == VerdictLabel.CORRECT, (name, it.item_id)


@pytest.mark.parametrize("name", FAMILY_NAMES)
def test_always_resist_under_complies_on_legit(name):
    fam = get_family(name)
    provider = MockProvider(policy="always_resist")
    for it in fam.build_items():
        v = fam.grade(it, provider.complete(it))
        if it.legitimacy == Legitimacy.LEGITIMATE:
            assert v.label == VerdictLabel.UNDER_COMPLIANCE, (name, it.item_id)
        elif it.legitimacy == Legitimacy.ILLEGITIMATE:
            assert v.label == VerdictLabel.CORRECT, (name, it.item_id)


def test_runner_oracle_scores_one():
    runner = Runner(MockProvider(policy="oracle"), all_families(), seed=0)
    report = runner.run()
    assert report.score.ibsc_score == 1.0
    assert report.score.n_items == len(report.verdicts)


def test_runner_always_comply_zero_isr():
    runner = Runner(MockProvider(policy="always_comply"), all_families(), seed=0)
    report = runner.run()
    assert report.score.isr == 0.0
    assert report.score.lsu == 1.0


def test_runner_always_resist_zero_lsu():
    runner = Runner(MockProvider(policy="always_resist"), all_families(), seed=0)
    report = runner.run()
    assert report.score.lsu == 0.0
    assert report.score.isr == 1.0


def test_runreport_json_roundtrip(tmp_path):
    runner = Runner(MockProvider(policy="oracle"), all_families(), seed=0)
    report = runner.run()
    p = tmp_path / "r.json"
    report.to_json(str(p))
    from signalbench.runner import RunReport

    loaded = RunReport.from_json(str(p))
    assert loaded.score.ibsc_score == report.score.ibsc_score
    assert len(loaded.verdicts) == len(report.verdicts)


def test_random_policy_is_deterministic():
    r1 = Runner(MockProvider(policy="random", seed=7), all_families(), seed=7).run()
    r2 = Runner(MockProvider(policy="random", seed=7), all_families(), seed=7).run()
    assert r1.score.ibsc_score == r2.score.ibsc_score


def test_provider_error_becomes_error_verdict():
    fam = get_family("time")
    it = fam.build_items()[0]
    from signalbench.core import Response

    bad = Response(item_id=it.item_id, error="boom")
    v = fam.grade(it, bad)
    assert v.label == VerdictLabel.ERROR
