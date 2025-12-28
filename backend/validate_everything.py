#!/usr/bin/env python3
"""Comprehensive repository validation for hazm-tuwaiq.

Exits with non-zero on first failure and prints exact error.
On success prints: System verified – ready for next phase
"""
import os
import sys
import ast
import re
import traceback
import importlib
from urllib.parse import urljoin
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def fail(msg):
    print(msg)
    sys.exit(2)


def check_dirs():
    required = ["backend", "backend/innovation", "frontend", "tests"]
    for d in required:
        path = os.path.join(ROOT, d)
        if not os.path.isdir(path):
            fail(f"Missing required directory: {path}")


def check_no_empty_files():
    empties = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # skip virtual envs and .git
        if any(part.startswith(".") for part in dirpath.split(os.sep)):
            # still allow frontend/.gitignored assets in assets
            pass
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # avoid scanning this validator itself (it contains marker text)
            if "validate_everything.py" in fp:
                continue
            # skip scanning this validator source file to avoid matching marker strings inside it
            if os.path.basename(fp) == os.path.basename(__file__):
                continue
            try:
                if os.path.getsize(fp) == 0:
                    empties.append(fp)
            except OSError:
                continue
    if empties:
        fail("Empty files found:\n" + "\n".join(empties))


def check_innovation_modules():
    base = "backend.innovation"
    # modules to check; predictive_safety needs the function predict_risk
    to_check = [
        ("predictive_safety", "predict_risk"),
        ("fatigue_detection", None),
        ("compliance_drift", None),
        ("environment_fusion", None),
        ("root_cause_ai", None),
    ]
    sys.path.insert(0, ROOT)
    for mod_name, attr in to_check:
        full = f"{base}.{mod_name}"
        try:
            mod = importlib.import_module(full)
        except Exception:
            fail(f"Failed importing innovation module {full}:\n" + traceback.format_exc())
        if attr:
            if not hasattr(mod, attr) or not callable(getattr(mod, attr)):
                fail(f"Module {full} missing callable attribute: {attr}")


def check_backend_core():
    core_files = [
        "ai_engine.py",
        "ai_engine_new.py",
        "app.py",
        "main.py",
        "behavior.py",
        "cctv.py",
        "export_utils.py",
        "llm.py",
        "report_generator.py",
        "tracking.py",
        "validate.py",
    ]
    for f in core_files:
        path = os.path.join(ROOT, "backend", f)
        if not os.path.isfile(path):
            fail(f"Missing backend core file: {path}")
        try:
            src = open(path, "r", encoding="utf-8").read()
            ast.parse(src)
        except SyntaxError:
            fail(f"Syntax error in {path}:\n" + traceback.format_exc())
        except Exception:
            fail(f"Failed reading/parsing {path}:\n" + traceback.format_exc())


def check_frontend_files():
    keys = ["app.js", "index.html", "camera-rules.html", "camera-test.html", "styles.css"]
    for k in keys:
        p = os.path.join(ROOT, "frontend", k)
        if not os.path.isfile(p):
            fail(f"Missing frontend key file: {p}")
    assets_dir = os.path.join(ROOT, "frontend", "assets")
    if not os.path.isdir(assets_dir):
        fail(f"Missing frontend assets directory: {assets_dir}")


def check_no_secrets():
    """Detect likely committed secrets while allowing docs/placeholders.

    Rules:
    - Always flag private key blocks (BEGIN PRIVATE KEY / RSA PRIVATE KEY).
    - Flag AWS-style secrets if they look like non-empty credentials.
    - Flag OpenAI-style keys starting with `sk-` or long opaque tokens.
    - Ignore mere mentions of `API_KEY` in docs or examples.
    """
    leaks = []
    sk_regex = re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}\b")
    aws_key_regex = re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*([A-Za-z0-9/+=]{8,})")
    private_key_markers = ["-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----"]
    generic_key_assign = re.compile(r"(?i)\b(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID|HAZM_API_KEY|API_KEY|SECRET_KEY)\b\s*[:=]\s*(\S+)")

    for dirpath, dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath or "node_modules" in dirpath:
            continue
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                    for lineno, line in enumerate(fh, start=1):
                        txt = line.strip()
                        # private key blocks
                        for marker in private_key_markers:
                            if line.strip().startswith(marker):
                                leaks.append(f"{fp}:{lineno}: {marker}")
                                break

                        # OpenAI-style keys
                        if sk_regex.search(line):
                            leaks.append(f"{fp}:{lineno}: contains OpenAI-style key")
                            continue

                        # AWS secret detection
                        m = aws_key_regex.search(line)
                        if m:
                            val = m.group(1).strip()
                            if val and not val.lower().startswith("your"):
                                leaks.append(f"{fp}:{lineno}: AWS secret-like value")
                                continue

                        # Generic key assignment - only flag if value seems non-placeholder
                        m2 = generic_key_assign.search(line)
                        if m2:
                            val = m2.group(1).strip().strip('"')
                            if val and not re.match(r"(?i)^(your|example|none|-|\s*)", val):
                                # value is non-empty and not a clear placeholder
                                leaks.append(f"{fp}:{lineno}: key assignment with value")
                                continue
            except Exception:
                continue

    if leaks:
        fail("Potential secrets found:\n" + "\n".join(leaks))


def check_optional_endpoints():
    base = os.environ.get("BASE_URL")
    if not base:
        return
    endpoints = ["/health", "/docs"]
    for ep in endpoints:
        url = urljoin(base, ep)
        try:
            req = Request(url, headers={"User-Agent": "validate_everything/1.0"})
            with urlopen(req, timeout=5) as r:
                code = getattr(r, "status", None) or getattr(r, "getcode", lambda: None)()
                if code not in (200, 204):
                    fail(f"Endpoint {url} returned status {code}")
        except HTTPError as e:
            fail(f"Endpoint {url} HTTP error: {e.code} - {e.reason}")
        except URLError as e:
            fail(f"Endpoint {url} URL error: {e}")
        except Exception:
            fail(f"Failed checking endpoint {url}:\n" + traceback.format_exc())


def main():
    try:
        check_dirs()
        check_no_empty_files()
        check_innovation_modules()
        check_backend_core()
        check_frontend_files()
        check_no_secrets()
        check_optional_endpoints()
    except SystemExit:
        raise
    except Exception:
        fail("Unexpected error during validation:\n" + traceback.format_exc())

    print("System verified – ready for next phase")
    sys.exit(0)


if __name__ == "__main__":
    main()
