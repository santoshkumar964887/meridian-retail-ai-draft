#!/usr/bin/env python3
"""
Setup environment file for Meridian Retail Support Draft Review Tool
"""
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"
DEFAULT_MODEL = "gpt-oss:20b-cloud"


def main():
    model = input(f"Enter Ollama model name [{DEFAULT_MODEL}]: ").strip()
    if not model:
        model = DEFAULT_MODEL

    ENV_FILE.write_text(f"OLLAMA_MODEL={model}\n")
    print(f"Written to {ENV_FILE}")


if __name__ == "__main__":
    main()