#!/usr/bin/env python3
"""Static contract checks for the Dolibarr/Medimo login template."""
from pathlib import Path
import re
import sys

import tinycss2

TEMPLATE = Path("core/tpl/login.tpl.php")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_css_rules(rules, where="stylesheet"):
    for rule in rules:
        if rule.type == "error":
            fail(f"CSS parse error in {where}: {rule.message}")
        if rule.type == "qualified-rule":
            declarations = tinycss2.parse_declaration_list(
                rule.content, skip_whitespace=True, skip_comments=True
            )
            for declaration in declarations:
                if declaration.type == "error":
                    fail(f"CSS declaration error in {where}: {declaration.message}")
        elif rule.type == "at-rule" and rule.content is not None:
            if rule.lower_at_keyword in {"media", "supports", "container", "layer", "document"}:
                nested = tinycss2.parse_rule_list(
                    rule.content, skip_whitespace=True, skip_comments=True
                )
                parse_css_rules(nested, f"@{rule.lower_at_keyword}")
            else:
                declarations = tinycss2.parse_declaration_list(
                    rule.content, skip_whitespace=True, skip_comments=True
                )
                for declaration in declarations:
                    if declaration.type == "error":
                        fail(f"CSS at-rule error in @{rule.lower_at_keyword}: {declaration.message}")


def main() -> None:
    if not TEMPLATE.is_file():
        fail(f"Missing {TEMPLATE}")
    source = TEMPLATE.read_text(encoding="utf-8")

    required = {
        'login POST form': r'<form\s+id="login"[^>]*method="post"',
        'CSRF token field': r'<input\s+type="hidden"\s+name="token"',
        'login action field': r'<input\s+type="hidden"\s+name="actionlogin"',
        'username field': r'name="username"',
        'password field': r'name="password"',
        'username icon': r'fa-user-circle',
        'password icon': r'fa-lock',
        'responsive tablet breakpoint': r'@media\s*\(max-width:\s*900px\)',
        'responsive mobile breakpoint': r'@media\s*\(max-width:\s*480px\)',
    }
    for label, pattern in required.items():
        if not re.search(pattern, source, flags=re.IGNORECASE):
            fail(f"Required login contract missing: {label}")

    style_blocks = re.findall(
        r'<style\b[^>]*>(.*?)</style\s*>', source, flags=re.IGNORECASE | re.DOTALL
    )
    if len(style_blocks) != 1:
        fail(f"Expected exactly one embedded login style block; found {len(style_blocks)}")

    rules = tinycss2.parse_stylesheet(
        style_blocks[0], skip_whitespace=True, skip_comments=True
    )
    parse_css_rules(rules, "login.tpl.php")

    print("PASS: login form, CSRF/action fields, username/password fields and responsive breakpoints are present.")
    print("PASS: embedded login CSS parsed without syntax errors.")


if __name__ == "__main__":
    main()
