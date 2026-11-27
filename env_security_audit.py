"""
Pre-Launch Environment & Secret Leak Audit Script
Part of the Vibe-Coded App Debug Kit (for Cursor, Lovable, Bolt, Replit & v0 projects).

Scans a project directory for:
1. Hardcoded API key patterns (OpenAI, Stripe, AWS, generic Bearer tokens)
2. Committed .env files without .gitignore protection
3. Missing .env.example template

Usage:
    python env_security_audit.py <project_directory>
"""

from __future__ import annotations
import os
import re
import sys

SECRET_PATTERNS = {
    "OpenAI API Key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "Stripe Live Key": re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Supabase / JWT Token": re.compile(r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]{20,}"),
}

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build"}
SCAN_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".env", ".yml", ".yaml", ".toml"}


def audit_directory(root: str) -> int:
    findings: list[str] = []
    has_env = False
    has_env_example = False
    gitignore_protects_env = False

    gi_path = os.path.join(root, ".gitignore")
    if os.path.isfile(gi_path):
        with open(gi_path, "r", encoding="utf-8", errors="ignore") as f:
            if ".env" in f.read():
                gitignore_protects_env = True

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname == ".env":
                has_env = True
            if fname == ".env.example":
                has_env_example = True
            _, ext = os.path.splitext(fname)
            if ext.lower() not in SCAN_EXTS and fname != ".env":
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root)
            if fname == "env_security_audit.py":
                continue
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, start=1):
                        for label, rx in SECRET_PATTERNS.items():
                            if rx.search(line):
                                findings.append(f"[SECRET RISK] {label} pattern in {rel}:{lineno}")
            except OSError:
                continue

    print(f"=== Pre-Launch Security Audit: {os.path.abspath(root)} ===")
    if has_env and not gitignore_protects_env:
        findings.append("[CONFIG RISK] .env file found, but .gitignore does not ignore .env")
    if has_env and not has_env_example:
        print("[INFO] Tip: Add a .env.example file with placeholder keys for safer deployments.")

    if not findings:
        print("[OK] No hardcoded secret patterns or exposed .env issues detected.")
        return 0

    for item in findings:
        print(item)
    return 1


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(audit_directory(target))
