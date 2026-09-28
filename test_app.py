#!/usr/bin/env python3
"""
Tests for app.py - no external API calls
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from app import (
    load_case,
    load_policy,
    load_demo_output,
    build_prompt,
    validate_response,
    unavailable_result,
    call_ollama,
)


def test_load_cases():
    for cid in ["C1", "C2", "C3"]:
        case = load_case(cid)
        assert case["case_id"] == cid
        assert "order_id" in case
        assert "customer_question" in case


def test_load_policy():
    policy = load_policy()
    assert "P1" in policy
    assert "P2" in policy
    assert "P3" in policy
    assert "P4" in policy


def test_load_demo_outputs():
    for cid in ["C1", "C2", "C3"]:
        demo = load_demo_output(cid)
        assert "draft_reply" in demo
        assert "evidence_refs" in demo
        assert "missing_information" in demo
        assert "review_status" in demo


def test_build_prompt_contains_facts_and_policy():
    case = load_case("C1")
    policy = load_policy()
    prompt = build_prompt(case, policy)
    assert "SUPPLIED FACTS" in prompt
    assert "SUPPLIED POLICY" in prompt
    assert "MR-1042" in prompt
    assert "P1" in prompt


def test_validate_response_success():
    valid = {
        "draft_reply": "test",
        "evidence_refs": ["P1"],
        "missing_information": [],
        "review_status": "READY_FOR_HUMAN_REVIEW",
    }
    assert validate_response(valid) == valid


def test_validate_response_missing_field():
    invalid = {"draft_reply": "test", "evidence_refs": [], "missing_information": []}
    assert validate_response(invalid) is None


def test_validate_response_wrong_type():
    invalid = {
        "draft_reply": "test",
        "evidence_refs": "not a list",
        "missing_information": [],
        "review_status": "READY_FOR_HUMAN_REVIEW",
    }
    assert validate_response(invalid) is None


def test_validate_response_invalid_status():
    invalid = {
        "draft_reply": "test",
        "evidence_refs": [],
        "missing_information": [],
        "review_status": "INVALID_STATUS",
    }
    assert validate_response(invalid) is None


def test_unavailable_result():
    result = unavailable_result("test reason")
    assert result["review_status"] == "UNAVAILABLE"
    assert result["draft_reply"] == ""
    assert "test reason" in result["_fallback"]


@patch("app.requests.post")
def test_call_ollama_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": '{"draft_reply": "ok", "evidence_refs": [], "missing_information": [], "review_status": "READY_FOR_HUMAN_REVIEW"}'}
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    result = call_ollama("test-model", "test prompt")
    assert result is not None
    assert result["draft_reply"] == "ok"


@patch("app.requests.post")
def test_call_ollama_failure(mock_post):
    mock_post.side_effect = Exception("connection error")
    result = call_ollama("test-model", "test prompt")
    assert result is None


def test_offline_demo_flag(capsys):
    from app import main
    with patch("sys.argv", ["app.py", "--case", "C1", "--offline-demo"]):
        main()
    captured = capsys.readouterr()
    assert "No model API was called" in captured.out
    assert "SUPPLIED FACTS" in captured.out


def test_simulate_timeout_flag(capsys):
    from app import main
    with patch("sys.argv", ["app.py", "--case", "C1", "--simulate-timeout"]):
        main()
    captured = capsys.readouterr()
    assert "UNAVAILABLE" in captured.out
    assert "Simulated timeout" in captured.out