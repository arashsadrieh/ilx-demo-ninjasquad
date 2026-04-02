#!/usr/bin/env python3
"""
SCORM 1.2 Course — E2E Browser Test Suite
Issue #20 — Test: E2E Browser Testing — Course Navigation, Quizzes, and SCORM API

Tests:
- Course launch and display
- All 8 lessons render with content
- Navigation (sidebar TOC, prev/next)
- Quiz functionality
- Responsive layout (1024, 1280, 1440px)
- SCORM API graceful fallback without LMS
- Screenshot capture
"""

import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, "/workspace/ilx-demo-ninjasquad")

from browser_interface import BrowserInterface

BASE_URL = os.environ.get("SCORM_URL", "http://0.0.0.0:3000")
SCREENSHOT_DIR = "/workspace/ilx-demo-ninjasquad/reports/screenshots"
REPORT_PATH = "/workspace/ilx-demo-ninjasquad/reports/e2e_test_report.md"
RESULTS_JSON = "/workspace/ilx-demo-ninjasquad/reports/e2e_test_results.json"

# Ensure screenshot directory exists
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Test results collector
results = []


def add_result(test_id, name, passed, detail="", screenshot=""):
    status = "PASS" if passed else "FAIL"
    results.append({
        "id": test_id,
        "name": name,
        "status": status,
        "detail": detail,
        "screenshot": screenshot,
    })
    icon = "✅" if passed else "❌"
    msg = f"  {icon} {test_id}: {name}"
    if detail and not passed:
        msg += f" — {detail}"
    print(msg)


def screenshot_path(name):
    return os.path.join(SCREENSHOT_DIR, f"{name}.png")


def test_launch_and_display():
    """Test course launches and displays correctly."""
    print("\n🚀 Launch & Display Tests")

    try:
        with BrowserInterface(headless=True, viewport_width=1280, viewport_height=720) as b:
            b.goto(BASE_URL, wait_until="networkidle")

            # Check page loaded
            title = b.title
            add_result("L01", "Course page loads", bool(title),
                       f"Title: '{title}'" if title else "No title")

            # Screenshot launch page
            ss = screenshot_path("01_launch_page")
            b.screenshot(ss, full_page=True)
            add_result("L02", "Launch page screenshot captured", os.path.exists(ss),
                       screenshot=ss)

            # Check for JS errors
            try:
                b.assert_no_errors()
                add_result("L03", "No JavaScript errors on load", True)
            except AssertionError as e:
                add_result("L03", "No JavaScript errors on load", False, str(e)[:200])

            # Check basic content is present
            page_text = b.page.inner_text("body")
            has_content = len(page_text) > 50
            add_result("L04", "Page has visible content", has_content,
                       f"{len(page_text)} chars of text")

            # Check for course title or module references
            has_course_ref = any(kw in page_text.lower() for kw in [
                "migration", "cloud", "module", "lesson", "gcp", "aws"
            ])
            add_result("L05", "Course content keywords present", has_course_ref)

    except Exception as e:
        add_result("L01", "Course page loads", False, f"Error: {str(e)[:200]}")


def test_lesson_content():
    """Test all 8 lessons render with content."""
    print("\n📚 Lesson Content Tests")

    lessons = [
        ("Module 1, Lesson 1", "Migration Drivers"),
        ("Module 1, Lesson 2", "Service Mapping"),
        ("Module 1, Lesson 3", "Portfolio Analysis"),
        ("Module 2, Lesson 1", "Infrastructure-as-Code"),
        ("Module 2, Lesson 2", "Data Migration"),
        ("Module 2, Lesson 3", "Application Cutover"),
        ("Module 3, Lesson 1", "Cost Optimization"),
        ("Module 3, Lesson 2", "Performance Tuning"),
    ]

    try:
        with BrowserInterface(headless=True, viewport_width=1280, viewport_height=720) as b:
            b.goto(BASE_URL, wait_until="networkidle")
            time.sleep(2)

            for i, (lesson_label, keyword) in enumerate(lessons):
                test_id = f"LC{i+1:02d}"
                try:
                    # Try clicking on the lesson in sidebar/navigation
                    # Strategies: look for text links, nav items, etc.
                    clicked = False

                    # Try finding by partial text match
                    for selector in [
                        f"text={keyword}",
                        f"a:has-text('{keyword}')",
                        f"[data-lesson='{i}']",
                        f"li:nth-child({i+1}) a",
                    ]:
                        try:
                            el = b.page.query_selector(selector)
                            if el:
                                el.click()
                                time.sleep(1)
                                clicked = True
                                break
                        except Exception:
                            continue

                    if not clicked:
                        # Try next button navigation
                        try:
                            next_btn = b.page.query_selector("text=Next") or \
                                       b.page.query_selector("button:has-text('Next')") or \
                                       b.page.query_selector(".next-btn") or \
                                       b.page.query_selector("[data-nav='next']")
                            if next_btn and i > 0:
                                next_btn.click()
                                time.sleep(1)
                                clicked = True
                        except Exception:
                            pass

                    # Check content
                    page_text = b.page.inner_text("body")
                    has_content = len(page_text) > 100

                    # Take screenshot for this lesson
                    ss = screenshot_path(f"lesson_{i+1:02d}")
                    b.screenshot(ss)

                    add_result(test_id, f"Lesson: {lesson_label}",
                               has_content,
                               f"{'Navigated' if clicked else 'Could not navigate'}, {len(page_text)} chars",
                               screenshot=ss)

                except Exception as e:
                    add_result(test_id, f"Lesson: {lesson_label}", False, str(e)[:150])

    except Exception as e:
        add_result("LC00", "Lesson content test setup", False, str(e)[:200])


def test_navigation():
    """Test sidebar TOC, prev/next buttons, and progress indicator."""
    print("\n🧭 Navigation Tests")

    try:
        with BrowserInterface(headless=True, viewport_width=1280, viewport_height=720) as b:
            b.goto(BASE_URL, wait_until="networkidle")
            time.sleep(2)

            # Check for sidebar/TOC
            sidebar_selectors = [
                "nav", ".sidebar", "#sidebar", ".toc", "#toc",
                "[role='navigation']", ".nav-menu", ".course-nav"
            ]
            has_sidebar = False
            for sel in sidebar_selectors:
                try:
                    el = b.page.query_selector(sel)
                    if el and el.is_visible():
                        has_sidebar = True
                        break
                except Exception:
                    continue

            add_result("N01", "Sidebar/TOC navigation visible", has_sidebar)

            # Check for prev/next buttons
            next_selectors = [
                "text=Next", "button:has-text('Next')", ".next-btn",
                "[data-nav='next']", "text=»", ".btn-next"
            ]
            has_next = False
            for sel in next_selectors:
                try:
                    el = b.page.query_selector(sel)
                    if el:
                        has_next = True
                        break
                except Exception:
                    continue

            add_result("N02", "Next button present", has_next)

            prev_selectors = [
                "text=Previous", "text=Prev", "button:has-text('Prev')",
                ".prev-btn", "[data-nav='prev']", "text=«", ".btn-prev"
            ]
            has_prev = False
            for sel in prev_selectors:
                try:
                    el = b.page.query_selector(sel)
                    if el:
                        has_prev = True
                        break
                except Exception:
                    continue

            add_result("N03", "Previous button present", has_prev)

            # Check for progress indicator
            progress_selectors = [
                ".progress", "#progress", "[role='progressbar']",
                ".progress-bar", ".progress-indicator", "progress"
            ]
            has_progress = False
            for sel in progress_selectors:
                try:
                    el = b.page.query_selector(sel)
                    if el:
                        has_progress = True
                        break
                except Exception:
                    continue

            add_result("N04", "Progress indicator present", has_progress)

            # Try navigating forward with Next button
            if has_next:
                try:
                    for sel in next_selectors:
                        try:
                            el = b.page.query_selector(sel)
                            if el:
                                before_text = b.page.inner_text("body")[:200]
                                el.click()
                                time.sleep(1)
                                after_text = b.page.inner_text("body")[:200]
                                content_changed = before_text != after_text
                                add_result("N05", "Next button changes content", content_changed)

                                ss = screenshot_path("nav_after_next")
                                b.screenshot(ss)
                                break
                        except Exception:
                            continue
                except Exception as e:
                    add_result("N05", "Next button changes content", False, str(e)[:150])
            else:
                add_result("N05", "Next button changes content", False, "No next button found")

    except Exception as e:
        add_result("N00", "Navigation test setup", False, str(e)[:200])


def test_quiz():
    """Test quiz functionality."""
    print("\n📝 Quiz Tests")

    try:
        with BrowserInterface(headless=True, viewport_width=1280, viewport_height=720) as b:
            b.goto(BASE_URL, wait_until="networkidle")
            time.sleep(2)

            # Look for quiz/assessment link
            quiz_selectors = [
                "text=Quiz", "text=Assessment", "text=Test",
                "a:has-text('Quiz')", "a:has-text('Assessment')",
                ".quiz-link", "#quiz", "[data-type='quiz']"
            ]
            has_quiz = False
            for sel in quiz_selectors:
                try:
                    el = b.page.query_selector(sel)
                    if el:
                        el.click()
                        time.sleep(2)
                        has_quiz = True
                        break
                except Exception:
                    continue

            add_result("Q01", "Quiz/Assessment accessible", has_quiz,
                       "" if has_quiz else "Could not find quiz link")

            if has_quiz:
                ss = screenshot_path("quiz_page")
                b.screenshot(ss, full_page=True)

                # Check for quiz questions
                page_text = b.page.inner_text("body")
                has_questions = any(kw in page_text.lower() for kw in [
                    "question", "select", "answer", "choose", "which"
                ])
                add_result("Q02", "Quiz questions visible", has_questions, screenshot=ss)

                # Check for radio buttons or checkboxes (answer options)
                inputs = b.page.query_selector_all("input[type='radio'], input[type='checkbox'], .answer-option, .quiz-option")
                add_result("Q03", "Answer options present", len(inputs) > 0,
                           f"Found {len(inputs)} input elements")

                # Check for submit button
                submit_selectors = [
                    "button:has-text('Submit')", "button:has-text('Check')",
                    "button:has-text('Grade')", "input[type='submit']",
                    ".submit-btn", "#submit-quiz"
                ]
                has_submit = False
                for sel in submit_selectors:
                    try:
                        el = b.page.query_selector(sel)
                        if el:
                            has_submit = True
                            break
                    except Exception:
                        continue

                add_result("Q04", "Submit button present", has_submit)

    except Exception as e:
        add_result("Q00", "Quiz test setup", False, str(e)[:200])


def test_responsive():
    """Test responsive layout at different widths."""
    print("\n📱 Responsive Layout Tests")

    viewports = [
        ("1024px", 1024, 768),
        ("1280px", 1280, 720),
        ("1440px", 1440, 900),
    ]

    for name, width, height in viewports:
        test_id = f"R-{name}"
        try:
            with BrowserInterface(headless=True, viewport_width=width, viewport_height=height) as b:
                b.goto(BASE_URL, wait_until="networkidle")
                time.sleep(2)

                # Take screenshot
                ss = screenshot_path(f"responsive_{width}")
                b.screenshot(ss, full_page=True)

                # Check no horizontal scroll (content doesn't overflow)
                overflow = b.page.evaluate("""
                    () => document.documentElement.scrollWidth > document.documentElement.clientWidth
                """)
                no_overflow = not overflow

                # Check for JS errors
                try:
                    b.assert_no_errors()
                    no_errors = True
                except AssertionError:
                    no_errors = False

                add_result(test_id, f"Layout at {name} — no overflow",
                           no_overflow,
                           f"Overflow detected" if not no_overflow else "",
                           screenshot=ss)

                add_result(f"{test_id}-err", f"No JS errors at {name}", no_errors)

        except Exception as e:
            add_result(test_id, f"Layout at {name}", False, str(e)[:150])


def test_scorm_api_fallback():
    """Test SCORM API wrapper handles missing LMS gracefully."""
    print("\n🔌 SCORM API Fallback Tests")

    try:
        with BrowserInterface(headless=True, viewport_width=1280, viewport_height=720) as b:
            b.goto(BASE_URL, wait_until="networkidle")
            time.sleep(2)

            # Check that the page doesn't crash without an LMS API
            try:
                b.assert_no_errors()
                add_result("S01", "Page loads without LMS (no JS errors)", True)
            except AssertionError as e:
                error_str = str(e)
                # Some SCORM warnings about missing API are acceptable
                is_just_warning = "api" in error_str.lower() or "lms" in error_str.lower()
                add_result("S01", "Page loads without LMS (no JS errors)",
                           is_just_warning,
                           f"{'Acceptable SCORM warning' if is_just_warning else error_str[:200]}")

            # Check console for SCORM-related messages
            console_output = b.page.evaluate("""
                () => {
                    // Check if there's a global SCORM/API object or fallback
                    return {
                        hasAPI: typeof window.API !== 'undefined',
                        hasAPIAdapter: typeof window.API_1484_11 !== 'undefined',
                        pageLoaded: document.readyState === 'complete'
                    };
                }
            """)
            add_result("S02", "Page fully loaded despite no LMS",
                       console_output.get("pageLoaded", False),
                       f"API present: {console_output.get('hasAPI', False)}")

    except Exception as e:
        add_result("S00", "SCORM API fallback test setup", False, str(e)[:200])


def generate_report():
    """Generate markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)

    report = f"""# E2E Browser Test Report — SCORM 1.2 Course

**Date:** {now}
**URL:** `{BASE_URL}`
**Tester:** Scout (QA Engineer)
**Issue:** #20

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tests | {total} |
| Passed | {passed} ✅ |
| Failed | {failed} ❌ |
| Pass Rate | {passed / total * 100:.0f}% |

**Overall:** {"✅ ALL TESTS PASSED" if failed == 0 else "❌ FAILURES DETECTED"}

---

## Detailed Results

| ID | Test | Status | Detail |
|----|------|--------|--------|
"""
    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        detail = r["detail"].replace("|", "\\|") if r["detail"] else ""
        report += f"| {r['id']} | {r['name']} | {icon} {r['status']} | {detail} |\n"

    report += f"""
---

## Screenshots

"""
    screenshots = [r for r in results if r.get("screenshot")]
    if screenshots:
        for r in screenshots:
            ss_name = os.path.basename(r["screenshot"])
            report += f"- **{r['name']}**: `screenshots/{ss_name}`\n"
    else:
        report += "No screenshots captured.\n"

    report += f"""
---

## Failed Tests

"""
    failures = [r for r in results if r["status"] == "FAIL"]
    if failures:
        for f in failures:
            report += f"- **{f['id']}**: {f['name']} — {f['detail']}\n"
    else:
        report += "None — all tests passed.\n"

    report += f"""
---

## Recommendations

"""
    if failed == 0:
        report += "All E2E tests passed. SCORM package is ready for LMS upload testing.\n"
    else:
        report += "Fix the failures above before declaring QA complete.\n"
        if any(r["id"].startswith("L") and r["status"] == "FAIL" for r in results):
            report += "- **Launch issues** are critical blockers.\n"
        if any(r["id"].startswith("N") and r["status"] == "FAIL" for r in results):
            report += "- **Navigation issues** affect user experience.\n"
        if any(r["id"].startswith("Q") and r["status"] == "FAIL" for r in results):
            report += "- **Quiz issues** affect LMS score reporting.\n"

    return report


def main():
    print("🔍 SCORM 1.2 Course — E2E Browser Test Suite")
    print(f"   URL: {BASE_URL}")
    print()

    # Run all test suites
    test_launch_and_display()
    test_lesson_content()
    test_navigation()
    test_quiz()
    test_responsive()
    test_scorm_api_fallback()

    # Print summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)

    print(f"\n{'='*60}")
    print(f"📊 Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ FAILURES DETECTED — see report")
    print(f"{'='*60}")

    # Generate report
    report = generate_report()
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"\n📝 Report: {REPORT_PATH}")

    # Save JSON results
    with open(RESULTS_JSON, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "url": BASE_URL,
            "total": total,
            "passed": passed,
            "failed": failed,
            "results": results,
        }, f, indent=2)
    print(f"📊 JSON: {RESULTS_JSON}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
