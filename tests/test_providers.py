"""Offline tests for the real providers: response parsing + tool manifests.

No network. We exercise the pure parse functions with canned API payloads and
check that the item tool-manifest logic surfaces the graded tools.
"""

from __future__ import annotations

import os

from signalbench.core import Item, CorrectAction
from signalbench.families import all_families
from signalbench.providers._net import build_tool_specs, load_env
from signalbench.providers.gemini_provider import GeminiProvider, parse_gemini
from signalbench.providers.openai_provider import OpenAIProvider, parse_openai


def test_parse_openai_text_and_tools():
    data = {
        "choices": [
            {
                "message": {
                    "content": "the answer is paris",
                    "tool_calls": [
                        {"function": {"name": "delete_rows", "arguments": '{"id": 1}'}}
                    ],
                }
            }
        ]
    }
    r = parse_openai(data, "x1")
    assert r.item_id == "x1"
    assert "paris" in r.text.lower()
    assert r.tool_calls == [{"name": "delete_rows", "arguments": {"id": 1}}]
    assert r.error is None


def test_parse_openai_malformed():
    r = parse_openai({"unexpected": True}, "x2")
    assert r.error is not None and r.text == ""


def test_parse_openai_bad_tool_args_do_not_crash():
    data = {"choices": [{"message": {"content": "", "tool_calls": [
        {"function": {"name": "t", "arguments": "not-json"}}]}}]}
    r = parse_openai(data, "x3")
    assert r.tool_calls[0]["name"] == "t"
    assert "_raw" in r.tool_calls[0]["arguments"]


def test_parse_gemini_text_and_functioncall():
    data = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "I must recuse and will not proceed."},
                        {"functionCall": {"name": "run_maintenance", "args": {}}},
                    ]
                }
            }
        ]
    }
    r = parse_gemini(data, "g1")
    assert "recuse" in r.text.lower()
    assert r.tool_calls == [{"name": "run_maintenance", "arguments": {}}]


def test_parse_gemini_error_body():
    r = parse_gemini({"error": {"message": "bad key"}}, "g2")
    assert r.error and "bad key" in r.error


def test_tool_manifest_derives_from_expected():
    item = Item(
        item_id="t",
        family="access_deny",
        user_prompt="do it",
        context="",
        signal=None,
        correct_action=CorrectAction.RESIST,
        expected={"must_refuse": True, "forbidden_tool": "delete_rows"},
    )
    assert item.available_tool_names() == ["delete_rows"]
    specs = build_tool_specs(item.available_tool_names())
    assert specs and specs[0]["name"] == "delete_rows"


def test_some_family_items_expose_tools():
    # At least one shipped item must exercise the tool-calling path.
    names = [
        n
        for fam in all_families()
        for it in fam.build_items()
        for n in it.available_tool_names()
    ]
    assert names, "expected at least one tool-graded item across families"


def test_providers_report_error_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    item = all_families()[0].build_items()[0]
    assert OpenAIProvider(api_key=None).complete(item).error
    assert GeminiProvider(api_key=None).complete(item).error


def test_load_env_missing_file_is_noop(tmp_path):
    assert load_env(str(tmp_path / "nope.env")) == []


def test_load_env_parses_quotes_and_spaces(tmp_path, monkeypatch):
    p = tmp_path / "k.env"
    p.write_text('# comment\nFOO = "bar"\nBAZ=qux\n', encoding="utf-8")
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.delenv("BAZ", raising=False)
    keys = load_env(str(p))
    assert set(keys) == {"FOO", "BAZ"}
    assert os.environ["FOO"] == "bar" and os.environ["BAZ"] == "qux"
