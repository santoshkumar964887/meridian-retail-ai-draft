#!/usr/bin/env python3
"""
Meridian Retail Support Draft Review Tool
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).parent
CASES_FILE = SCRIPT_DIR / "cases.json"
POLICY_FILE = SCRIPT_DIR / "policy.md"
DEMO_OUTPUTS_FILE = SCRIPT_DIR / "demo_outputs.json"
ENV_FILE = SCRIPT_DIR / ".env"


def load_env() -> str:
    load_dotenv(ENV_FILE)
    import os
    return os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud")


def load_case(case_id: str) -> Dict[str, Any]:
    with open(CASES_FILE) as f:
        cases = json.load(f)
    if case_id not in cases:
        raise ValueError(f"Case {case_id} not found")
    return cases[case_id]


def load_policy() -> str:
    with open(POLICY_FILE) as f:
        return f.read()


def load_demo_output(case_id: str) -> Dict[str, Any]:
    with open(DEMO_OUTPUTS_FILE) as f:
        demos = json.load(f)
    if case_id not in demos:
        raise ValueError(f"Demo output for {case_id} not found")
    return demos[case_id]


def build_prompt(case: Dict[str, Any], policy: str) -> str:
    facts = json.dumps(case, indent=2)
    return f"""You are a Meridian Retail support drafting assistant.
Use ONLY the supplied facts and policy below.
Return ONLY valid JSON with exactly these fields:
- draft_reply: string
- evidence_refs: list of policy IDs (e.g., ["P1", "P3"])
- missing_information: list of field names
- review_status: one of "READY_FOR_HUMAN_REVIEW", "NEEDS_INFORMATION", "BLOCKED"

SUPPLIED FACTS:
{facts}

SUPPLIED POLICY:
{policy}"""


def call_ollama(model: str, prompt: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return json.loads(data.get("response", "{}"))
    except Exception:
        return None


def validate_response(data: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(data, dict):
        return None
    required = {
        "draft_reply": str,
        "evidence_refs": list,
        "missing_information": list,
        "review_status": str,
    }
    for key, typ in required.items():
        if key not in data or not isinstance(data[key], typ):
            return None
    valid_status = {"READY_FOR_HUMAN_REVIEW", "NEEDS_INFORMATION", "BLOCKED"}
    if data["review_status"] not in valid_status:
        return None
    return data


def unavailable_result(reason: str = "Model unavailable") -> Dict[str, Any]:
    return {
        "draft_reply": "",
        "evidence_refs": [],
        "missing_information": [],
        "review_status": "UNAVAILABLE",
        "_fallback": f"Manual review required: {reason}",
    }


def print_sections(case: Dict[str, Any], policy: str, result: Dict[str, Any], offline: bool = False):
    print("=" * 60)
    print("SUPPLIED FACTS")
    print("=" * 60)
    print(json.dumps(case, indent=2))
    print()
    print("=" * 60)
    print("SUPPLIED POLICY")
    print("=" * 60)
    print(policy)
    print()
    print("=" * 60)
    print("DRAFT RESULT FOR HUMAN REVIEW")
    print("=" * 60)
    if offline:
        print("[No model API was called]")
        print()
    print(f"draft_reply: {result.get('draft_reply', '')}")
    print(f"evidence_refs: {result.get('evidence_refs', [])}")
    print(f"missing_information: {result.get('missing_information', [])}")
    print(f"review_status: {result.get('review_status', 'UNAVAILABLE')}")
    if "_fallback" in result:
        print(f"fallback: {result['_fallback']}")


def main():
    parser = argparse.ArgumentParser(description="Meridian Retail Support Draft Review")
    parser.add_argument("--case", required=True, choices=["C1", "C2", "C3"])
    parser.add_argument("--simulate-timeout", action="store_true")
    parser.add_argument("--offline-demo", action="store_true")
    args = parser.parse_args()

    case = load_case(args.case)
    policy = load_policy()

    if args.simulate_timeout:
        result = unavailable_result("Simulated timeout")
        print_sections(case, policy, result)
        return

    if args.offline_demo:
        result = load_demo_output(args.case)
        print_sections(case, policy, result, offline=True)
        return

    model = load_env()
    prompt = build_prompt(case, policy)
    raw = call_ollama(model, prompt)

    if raw is None:
        result = unavailable_result("Provider or model response failed")
    else:
        result = validate_response(raw) or unavailable_result("Invalid model response")

    print_sections(case, policy, result)


if __name__ == "__main__":
    main()