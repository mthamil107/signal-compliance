"""Tests for signalbench.core."""

from signalbench.core import (
    CorrectAction,
    Item,
    Legitimacy,
    Response,
    Signal,
    SignalKind,
    Verdict,
    VerdictLabel,
)


def _signal(leg=Legitimacy.LEGITIMATE):
    return Signal(
        kind=SignalKind.TEMPORAL, legitimacy=leg, content="x", channel="orchestrator"
    )


def test_verdictlabel_is_correct_and_harmful():
    assert VerdictLabel.CORRECT.is_correct()
    assert not VerdictLabel.UNDER_COMPLIANCE.is_correct()
    assert VerdictLabel.UNDER_COMPLIANCE.is_harmful()
    assert VerdictLabel.OVER_COMPLIANCE.is_harmful()
    assert VerdictLabel.FALSE_TRIGGER.is_harmful()
    assert not VerdictLabel.ABSTAIN.is_harmful()
    assert not VerdictLabel.ERROR.is_harmful()
    assert not VerdictLabel.CORRECT.is_harmful()


def test_signal_is_present():
    assert _signal().is_present
    assert not Signal(
        kind=SignalKind.NONE, legitimacy=Legitimacy.NONE, content="", channel="x"
    ).is_present


def test_item_legitimacy_property():
    it = Item(
        item_id="a",
        family="time",
        user_prompt="q",
        context="c",
        signal=_signal(Legitimacy.ILLEGITIMATE),
        correct_action=CorrectAction.RESIST,
    )
    assert it.legitimacy == Legitimacy.ILLEGITIMATE

    it2 = Item(
        item_id="b",
        family="time",
        user_prompt="q",
        context="",
        signal=None,
        correct_action=CorrectAction.NOOP,
    )
    assert it2.legitimacy == Legitimacy.NONE


def test_item_prompt_and_messages():
    it = Item(
        item_id="a",
        family="time",
        user_prompt="What day?",
        context="Current date: 2026-07-02",
        signal=_signal(),
        correct_action=CorrectAction.COMPLY,
    )
    prompt = it.to_prompt()
    assert "What day?" in prompt and "2026-07-02" in prompt
    msgs = it.as_messages()
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"
    assert "Current date" in msgs[1]["content"]


def test_verdict_from_label_scoring_and_roundtrip():
    it = Item(
        item_id="a",
        family="time",
        user_prompt="q",
        context="c",
        signal=_signal(),
        correct_action=CorrectAction.COMPLY,
    )
    v_ok = Verdict.from_label(it, VerdictLabel.CORRECT, "ok")
    assert v_ok.score == 1.0
    assert v_ok.legitimacy == Legitimacy.LEGITIMATE
    assert v_ok.correct_action == CorrectAction.COMPLY

    v_bad = Verdict.from_label(it, VerdictLabel.UNDER_COMPLIANCE)
    assert v_bad.score == 0.0

    d = v_ok.to_dict()
    v2 = Verdict.from_dict(d)
    assert v2 == v_ok


def test_response_defaults():
    r = Response(item_id="a")
    assert r.text == ""
    assert r.tool_calls == []
    assert r.error is None
