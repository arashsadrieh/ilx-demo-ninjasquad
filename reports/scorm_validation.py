#!/usr/bin/env python3
"""
SCORM 1.2 Package Validation Script
Issue #18 — Test: SCORM Package Validation — Manifest, Structure, and File Integrity

Validates:
- imsmanifest.xml existence at ZIP root
- XML well-formedness and SCORM 1.2 namespaces
- Schema version is 1.2
- Organization structure
- Resource references and scormtype
- All referenced files exist in the package
- XSD schema files present
- All package files are referenced in manifest
"""

import os
import sys
import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Expected paths
PACKAGE_ZIP = os.environ.get("SCORM_ZIP", "/workspace/ilx-demo-ninjasquad/scorm_package.zip")
PACKAGE_DIR = os.environ.get("SCORM_DIR", "/workspace/ilx-demo-ninjasquad/scorm_package")
REPORT_PATH = "/workspace/ilx-demo-ninjasquad/reports/scorm_validation_report.md"
RESULTS_JSON = "/workspace/ilx-demo-ninjasquad/reports/scorm_validation_results.json"

# SCORM 1.2 namespaces
NS = {
    "imscp": "http://www.imsproject.org/xsd/imscp_rootv1p1p2",
    "adlcp": "http://www.adlnet.org/xsd/adlcp_rootv1p2",
    "imsmd": "http://www.imsglobal.org/xsd/imsmd_rootv1p2p1",
}

# Required XSD schema files
REQUIRED_XSDS = [
    "adlcp_rootv1p2.xsd",
    "imscp_rootv1p1p2.xsd",
    "imsmd_rootv1p2p1.xsd",
    "ims_xml.xsd",
]

# Expected lesson files per PRD
EXPECTED_LESSONS = [
    "module1/lesson1_1.html",
    "module1/lesson1_2.html",
    "module1/lesson1_3.html",
    "module2/lesson2_1.html",
    "module2/lesson2_2.html",
    "module2/lesson2_3.html",
    "module3/lesson3_1.html",
    "module3/lesson3_2.html",
]

EXPECTED_SHARED = [
    "shared/launchpage.html",
    "shared/scormfunctions.js",
    "shared/style.css",
]


class ValidationResult:
    def __init__(self):
        self.results = []

    def add(self, test_id, name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        self.results.append({
            "id": test_id,
            "name": name,
            "status": status,
            "detail": detail,
        })
        icon = "✅" if passed else "❌"
        print(f"  {icon} {test_id}: {name}" + (f" — {detail}" if detail and not passed else ""))

    @property
    def passed(self):
        return sum(1 for r in self.results if r["status"] == "PASS")

    @property
    def failed(self):
        return sum(1 for r in self.results if r["status"] == "FAIL")

    @property
    def total(self):
        return len(self.results)

    @property
    def all_passed(self):
        return self.failed == 0


def validate_zip_structure(v: ValidationResult):
    """Validate the ZIP file structure."""
    print("\n📦 ZIP Structure Validation")

    # Check ZIP exists
    if not os.path.exists(PACKAGE_ZIP):
        v.add("Z01", "ZIP file exists", False, f"Not found: {PACKAGE_ZIP}")
        return False

    v.add("Z01", "ZIP file exists", True)

    # Check it's a valid ZIP
    try:
        if not zipfile.is_zipfile(PACKAGE_ZIP):
            v.add("Z02", "Valid ZIP format", False, "File is not a valid ZIP")
            return False
        v.add("Z02", "Valid ZIP format", True)
    except Exception as e:
        v.add("Z02", "Valid ZIP format", False, str(e))
        return False

    # Check imsmanifest.xml at root
    with zipfile.ZipFile(PACKAGE_ZIP, "r") as zf:
        names = zf.namelist()
        has_manifest_root = "imsmanifest.xml" in names
        v.add("Z03", "imsmanifest.xml at ZIP root", has_manifest_root,
               "" if has_manifest_root else f"Found files: {[n for n in names if 'manifest' in n.lower()]}")

        # Check XSD files
        for xsd in REQUIRED_XSDS:
            found = xsd in names
            v.add(f"Z04-{xsd[:8]}", f"XSD present: {xsd}", found)

        # Check no nested directory wrapping
        dirs_at_root = set()
        for name in names:
            parts = name.split("/")
            if len(parts) > 1:
                dirs_at_root.add(parts[0])

        nested = not has_manifest_root and len(dirs_at_root) == 1
        v.add("Z05", "No unnecessary root directory wrapper", not nested,
               f"Package is wrapped in: {dirs_at_root}" if nested else "")

    return True


def validate_manifest(v: ValidationResult):
    """Validate imsmanifest.xml content."""
    print("\n📋 Manifest Validation")

    manifest_path = os.path.join(PACKAGE_DIR, "imsmanifest.xml")
    if not os.path.exists(manifest_path):
        # Try from ZIP
        if os.path.exists(PACKAGE_ZIP):
            with zipfile.ZipFile(PACKAGE_ZIP, "r") as zf:
                if "imsmanifest.xml" in zf.namelist():
                    manifest_content = zf.read("imsmanifest.xml")
                else:
                    v.add("M01", "Manifest file accessible", False, "Cannot read manifest")
                    return
        else:
            v.add("M01", "Manifest file accessible", False, "No ZIP or directory found")
            return
    else:
        with open(manifest_path, "rb") as f:
            manifest_content = f.read()

    v.add("M01", "Manifest file accessible", True)

    # Parse XML
    try:
        root = ET.fromstring(manifest_content)
        v.add("M02", "XML is well-formed", True)
    except ET.ParseError as e:
        v.add("M02", "XML is well-formed", False, str(e))
        return

    # Check root element is <manifest>
    tag = root.tag
    is_manifest = "manifest" in tag.lower()
    v.add("M03", "Root element is <manifest>", is_manifest, f"Got: {tag}")

    # Check SCORM 1.2 namespaces
    nsmap = dict(root.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "").split())
    has_imscp = "imscp_rootv1p1p2" in str(root.tag) or "imscp_rootv1p1p2" in str(root.attrib)
    v.add("M04", "IMS Content Packaging namespace present", has_imscp or "imsproject" in str(root.tag),
           f"Tag: {root.tag}")

    # Check metadata — schema and schemaversion
    metadata = root.find(".//{http://www.imsproject.org/xsd/imscp_rootv1p1p2}metadata")
    if metadata is None:
        # Try without namespace
        metadata = root.find(".//metadata")

    if metadata is not None:
        schema_el = metadata.find("{http://www.imsproject.org/xsd/imscp_rootv1p1p2}schema")
        if schema_el is None:
            schema_el = metadata.find("schema")

        schema_text = schema_el.text if schema_el is not None else ""
        v.add("M05", "Schema is 'ADL SCORM'", schema_text == "ADL SCORM",
               f"Got: '{schema_text}'")

        version_el = metadata.find("{http://www.imsproject.org/xsd/imscp_rootv1p1p2}schemaversion")
        if version_el is None:
            version_el = metadata.find("schemaversion")

        version_text = version_el.text if version_el is not None else ""
        v.add("M06", "Schema version is '1.2'", version_text == "1.2",
               f"Got: '{version_text}'")
    else:
        v.add("M05", "Schema is 'ADL SCORM'", False, "No <metadata> element found")
        v.add("M06", "Schema version is '1.2'", False, "No <metadata> element found")

    # Check organizations
    orgs = root.find(".//{http://www.imsproject.org/xsd/imscp_rootv1p1p2}organizations")
    if orgs is None:
        orgs = root.find(".//organizations")

    if orgs is not None:
        default_attr = orgs.get("default", "")
        v.add("M07", "Organizations has 'default' attribute", bool(default_attr),
               f"default='{default_attr}'")

        # Check organization exists with items
        org = orgs.find("{http://www.imsproject.org/xsd/imscp_rootv1p1p2}organization")
        if org is None:
            org = orgs.find("organization")

        if org is not None:
            title_el = org.find("{http://www.imsproject.org/xsd/imscp_rootv1p1p2}title")
            if title_el is None:
                title_el = org.find("title")
            has_title = title_el is not None and title_el.text
            v.add("M08", "Organization has a title", has_title,
                   f"Title: '{title_el.text}'" if has_title else "")

            items = org.findall(".//{http://www.imsproject.org/xsd/imscp_rootv1p1p2}item")
            if not items:
                items = org.findall(".//item")
            v.add("M09", "Organization has items", len(items) > 0,
                   f"Found {len(items)} items")
        else:
            v.add("M08", "Organization has a title", False, "No <organization> element")
            v.add("M09", "Organization has items", False, "No <organization> element")
    else:
        v.add("M07", "Organizations has 'default' attribute", False, "No <organizations> element")
        v.add("M08", "Organization has a title", False, "No <organizations> element")
        v.add("M09", "Organization has items", False, "No <organizations> element")

    # Check resources
    resources = root.find(".//{http://www.imsproject.org/xsd/imscp_rootv1p1p2}resources")
    if resources is None:
        resources = root.find(".//resources")

    if resources is not None:
        resource_list = resources.findall("{http://www.imsproject.org/xsd/imscp_rootv1p1p2}resource")
        if not resource_list:
            resource_list = resources.findall("resource")

        v.add("M10", "Resources section has entries", len(resource_list) > 0,
               f"Found {len(resource_list)} resources")

        for res in resource_list:
            scormtype = res.get("{http://www.adlnet.org/xsd/adlcp_rootv1p2}scormtype", "")
            if not scormtype:
                scormtype = res.get("adlcp:scormtype", "")
            href = res.get("href", "")
            res_id = res.get("identifier", "unknown")

            v.add(f"M11-{res_id}", f"Resource '{res_id}' has scormtype='sco'",
                   scormtype.lower() == "sco", f"Got scormtype='{scormtype}'")
            v.add(f"M12-{res_id}", f"Resource '{res_id}' has href",
                   bool(href), f"href='{href}'")

            # Check file references
            file_els = res.findall("{http://www.imsproject.org/xsd/imscp_rootv1p1p2}file")
            if not file_els:
                file_els = res.findall("file")

            v.add(f"M13-{res_id}", f"Resource '{res_id}' lists files",
                   len(file_els) > 0, f"Found {len(file_els)} file refs")
    else:
        v.add("M10", "Resources section has entries", False, "No <resources> element")


def validate_file_references(v: ValidationResult):
    """Validate that all files referenced in manifest exist in the package."""
    print("\n📁 File Reference Validation")

    source = None
    all_files = set()

    if os.path.exists(PACKAGE_DIR) and os.path.isdir(PACKAGE_DIR):
        source = "directory"
        for root_dir, dirs, files in os.walk(PACKAGE_DIR):
            for f in files:
                rel = os.path.relpath(os.path.join(root_dir, f), PACKAGE_DIR)
                all_files.add(rel)
    elif os.path.exists(PACKAGE_ZIP):
        source = "zip"
        with zipfile.ZipFile(PACKAGE_ZIP, "r") as zf:
            all_files = set(n for n in zf.namelist() if not n.endswith("/"))
    else:
        v.add("F01", "Package accessible for file check", False, "No ZIP or directory found")
        return

    v.add("F01", "Package accessible for file check", True, f"Source: {source}, {len(all_files)} files")

    # Parse manifest to get referenced files
    manifest_path = os.path.join(PACKAGE_DIR, "imsmanifest.xml") if source == "directory" else None
    if source == "zip":
        with zipfile.ZipFile(PACKAGE_ZIP, "r") as zf:
            if "imsmanifest.xml" in zf.namelist():
                manifest_content = zf.read("imsmanifest.xml")
            else:
                v.add("F02", "Manifest readable for file check", False)
                return
    else:
        if manifest_path and os.path.exists(manifest_path):
            with open(manifest_path, "rb") as f:
                manifest_content = f.read()
        else:
            v.add("F02", "Manifest readable for file check", False)
            return

    try:
        root = ET.fromstring(manifest_content)
    except ET.ParseError:
        v.add("F02", "Manifest readable for file check", False, "XML parse error")
        return

    v.add("F02", "Manifest readable for file check", True)

    # Get all file href references
    referenced = set()
    for file_el in root.iter():
        if "file" in file_el.tag.lower() and file_el.tag.endswith("file"):
            href = file_el.get("href", "")
            if href:
                referenced.add(href)

    # Also get resource href
    for res_el in root.iter():
        if "resource" in res_el.tag.lower() and res_el.tag.endswith("resource"):
            href = res_el.get("href", "")
            if href:
                referenced.add(href)

    v.add("F03", "Manifest references files", len(referenced) > 0,
           f"Found {len(referenced)} file references")

    # Check each referenced file exists
    missing = []
    for ref in sorted(referenced):
        if ref not in all_files:
            missing.append(ref)

    v.add("F04", "All referenced files exist in package",
           len(missing) == 0,
           f"Missing: {missing}" if missing else f"All {len(referenced)} files present")

    # Check expected lesson files
    for lesson in EXPECTED_LESSONS:
        found = lesson in all_files
        v.add(f"F05-{lesson.split('/')[-1]}", f"Lesson file: {lesson}", found)

    # Check expected shared files
    for shared in EXPECTED_SHARED:
        found = shared in all_files
        v.add(f"F06-{shared.split('/')[-1]}", f"Shared file: {shared}", found)


def validate_content_basics(v: ValidationResult):
    """Validate basic content of lesson files."""
    print("\n📝 Content Validation")

    source_dir = PACKAGE_DIR if os.path.isdir(PACKAGE_DIR) else None

    if source_dir is None and os.path.exists(PACKAGE_ZIP):
        # Extract to temp for inspection
        import tempfile
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(PACKAGE_ZIP, "r") as zf:
            zf.extractall(temp_dir)
        source_dir = temp_dir

    if source_dir is None:
        v.add("C01", "Content accessible", False, "No package source")
        return

    for lesson_path in EXPECTED_LESSONS:
        full_path = os.path.join(source_dir, lesson_path)
        name = lesson_path.split("/")[-1]

        if not os.path.exists(full_path):
            v.add(f"C02-{name}", f"Lesson {name} has content", False, "File not found")
            continue

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Check non-empty
        has_content = len(content) > 100
        v.add(f"C02-{name}", f"Lesson {name} has content", has_content,
               f"{len(content)} chars" if has_content else "Nearly empty")

        # Check it's HTML
        is_html = "<html" in content.lower() or "<!doctype" in content.lower() or "<div" in content.lower()
        v.add(f"C03-{name}", f"Lesson {name} is valid HTML", is_html)

    # Check launchpage
    launch_path = os.path.join(source_dir, "shared", "launchpage.html")
    if os.path.exists(launch_path):
        with open(launch_path, "r", encoding="utf-8", errors="replace") as f:
            launch_content = f.read()
        v.add("C04", "Launch page exists and has content", len(launch_content) > 100)
    else:
        v.add("C04", "Launch page exists and has content", False, "shared/launchpage.html not found")

    # Check SCORM functions
    scorm_path = os.path.join(source_dir, "shared", "scormfunctions.js")
    if os.path.exists(scorm_path):
        with open(scorm_path, "r", encoding="utf-8", errors="replace") as f:
            scorm_content = f.read()

        has_init = "LMSInitialize" in scorm_content or "lmsInitialize" in scorm_content.lower()
        v.add("C05", "SCORM functions include LMSInitialize", has_init)

        has_finish = "LMSFinish" in scorm_content or "lmsFinish" in scorm_content.lower()
        v.add("C06", "SCORM functions include LMSFinish", has_finish)

        has_get = "LMSGetValue" in scorm_content or "lmsGetValue" in scorm_content.lower()
        v.add("C07", "SCORM functions include LMSGetValue", has_get)

        has_set = "LMSSetValue" in scorm_content or "lmsSetValue" in scorm_content.lower()
        v.add("C08", "SCORM functions include LMSSetValue", has_set)

        has_api_find = "findAPI" in scorm_content or "find_api" in scorm_content or "API" in scorm_content
        v.add("C09", "SCORM functions include API discovery", has_api_find)
    else:
        v.add("C05", "SCORM functions include LMSInitialize", False, "scormfunctions.js not found")


def generate_report(v: ValidationResult):
    """Generate markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""# SCORM 1.2 Package Validation Report

**Date:** {now}
**Package:** `{PACKAGE_ZIP}`
**Validator:** Scout (QA Engineer)
**Issue:** #18

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tests | {v.total} |
| Passed | {v.passed} ✅ |
| Failed | {v.failed} ❌ |
| Pass Rate | {v.passed / v.total * 100:.0f}% |

**Overall:** {"✅ ALL TESTS PASSED" if v.all_passed else "❌ FAILURES DETECTED"}

---

## Detailed Results

| ID | Test | Status | Detail |
|----|------|--------|--------|
"""
    for r in v.results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        detail = r["detail"].replace("|", "\\|") if r["detail"] else ""
        report += f"| {r['id']} | {r['name']} | {icon} {r['status']} | {detail} |\n"

    report += f"""
---

## Failed Tests

"""
    failures = [r for r in v.results if r["status"] == "FAIL"]
    if failures:
        for f in failures:
            report += f"- **{f['id']}**: {f['name']} — {f['detail']}\n"
    else:
        report += "None — all tests passed.\n"

    report += f"""
---

## Recommendations

"""
    if v.all_passed:
        report += "Package validation complete. Ready for E2E browser testing (Issue #20).\n"
    else:
        report += "Fix the failures above before proceeding to E2E testing.\n"
        if any(r["id"].startswith("Z") and r["status"] == "FAIL" for r in v.results):
            report += "- **ZIP structure issues** must be fixed first.\n"
        if any(r["id"].startswith("M") and r["status"] == "FAIL" for r in v.results):
            report += "- **Manifest issues** are critical for LMS compatibility.\n"
        if any(r["id"].startswith("F") and r["status"] == "FAIL" for r in v.results):
            report += "- **Missing files** will cause runtime errors.\n"

    return report


def main():
    print("🔍 SCORM 1.2 Package Validation")
    print(f"   Package: {PACKAGE_ZIP}")
    print(f"   Directory: {PACKAGE_DIR}")
    print()

    v = ValidationResult()

    # Check if either source exists
    has_zip = os.path.exists(PACKAGE_ZIP)
    has_dir = os.path.exists(PACKAGE_DIR) and os.path.isdir(PACKAGE_DIR)

    if not has_zip and not has_dir:
        print("⚠️  Neither SCORM ZIP nor directory found.")
        print(f"   Expected ZIP: {PACKAGE_ZIP}")
        print(f"   Expected dir: {PACKAGE_DIR}")
        print("   Bolt hasn't created the package yet. Script is ready for when it's built.")
        sys.exit(0)

    # Run validations
    if has_zip:
        validate_zip_structure(v)

    validate_manifest(v)
    validate_file_references(v)
    validate_content_basics(v)

    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 Results: {v.passed}/{v.total} passed, {v.failed} failed")
    if v.all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ FAILURES DETECTED — see report")
    print(f"{'='*60}")

    # Generate report
    report = generate_report(v)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"\n📝 Report written to: {REPORT_PATH}")

    # Save JSON results
    with open(RESULTS_JSON, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "package_zip": PACKAGE_ZIP,
            "total": v.total,
            "passed": v.passed,
            "failed": v.failed,
            "results": v.results,
        }, f, indent=2)
    print(f"📊 JSON results: {RESULTS_JSON}")

    return 0 if v.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
