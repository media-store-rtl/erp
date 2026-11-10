#!/usr/bin/env python3
"""Optional Playwright smoke test against an isolated ERP preview URL.

This test never submits credentials. Production hosts are explicitly rejected.
"""
import os
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

url = os.environ.get("ERP_PREVIEW_URL", "").strip()
if not url:
    raise SystemExit("ERP_PREVIEW_URL is required")

parsed = urlparse(url)
if parsed.scheme != "https" or not parsed.hostname:
    raise SystemExit("ERP_PREVIEW_URL must be an HTTPS URL")
host = parsed.hostname.lower()
if host in {"erp.mymedimo.ir", "mymedimo.ir", "www.mymedimo.ir"}:
    raise SystemExit("Refusing to run browser smoke test against production mymedimo.ir")

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={"width": 1365, "height": 900})
    response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
    if response is None or response.status >= 400:
        browser.close()
        raise SystemExit(f"Preview returned an invalid HTTP response: {response.status if response else 'none'}")

    form = page.locator("form#login")
    form.wait_for(state="visible")
    page.locator('input[name="username"]').wait_for(state="visible")
    page.locator('input[name="password"]').wait_for(state="visible")
    token = page.locator('input[name="token"]').get_attribute("value")
    action = page.locator('input[name="actionlogin"]').get_attribute("value")
    if not token:
        browser.close()
        raise SystemExit("CSRF token field is empty")
    if action != "login":
        browser.close()
        raise SystemExit(f"Unexpected actionlogin value: {action!r}")
    if (form.get_attribute("method") or "get").lower() != "post":
        browser.close()
        raise SystemExit("Login form must submit with POST")

    desktop_width = page.evaluate("document.documentElement.scrollWidth")
    if desktop_width > 1367:
        browser.close()
        raise SystemExit(f"Unexpected horizontal overflow on desktop: {desktop_width}px")

    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(300)
    if not form.is_visible():
        browser.close()
        raise SystemExit("Login form is not visible at mobile width")
    mobile_width = page.evaluate("document.documentElement.scrollWidth")
    if mobile_width > 392:
        browser.close()
        raise SystemExit(f"Unexpected horizontal overflow on mobile: {mobile_width}px")

    print("PASS: preview login form, fields, CSRF token, POST method and actionlogin checked.")
    print("PASS: login form remains visible at desktop and mobile viewport widths.")
    print("NOTE: no credentials were submitted; authentication success is not covered.")
    browser.close()
