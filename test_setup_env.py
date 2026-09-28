#!/usr/bin/env python3
"""
Tests for setup_env.py - no external API calls
"""
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

sys.path.insert(0, str(Path(__file__).parent))

from setup_env import main as setup_main, DEFAULT_MODEL, ENV_FILE


def test_setup_env_writes_key(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    monkeypatch.setattr("setup_env.ENV_FILE", env_file)

    with patch("builtins.input", return_value="custom-model"):
        setup_main()

    content = env_file.read_text()
    assert content == "OLLAMA_MODEL=custom-model\n"


def test_setup_env_default_model(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    monkeypatch.setattr("setup_env.ENV_FILE", env_file)

    with patch("builtins.input", return_value=""):
        setup_main()

    content = env_file.read_text()
    assert content == f"OLLAMA_MODEL={DEFAULT_MODEL}\n"


def test_setup_env_does_not_print_key(monkeypatch, tmp_path, capsys):
    env_file = tmp_path / ".env"
    monkeypatch.setattr("setup_env.ENV_FILE", env_file)

    with patch("builtins.input", return_value="secret-model"):
        setup_main()

    captured = capsys.readouterr()
    assert "secret-model" not in captured.out
    assert "Written to" in captured.out