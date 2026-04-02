# PRD: SCORM 1.2 Course Package — Cloud Computing Multi-Cloud Migration Strategy

## 1. Overview

**Project:** Convert the Ninja Academy course "Cloud Computing: Multi-Cloud Migration Strategy — GCP to AWS Platform Transition" into a fully compliant SCORM 1.2 content package (.zip) that can be imported into any SCORM-compliant LMS.

**Source Content:** https://ninja-academy.builtbyninja.com/courses/cloud-computing-multi-cloud-migration-strategy-gcp-to-aws-platform-transition

**SCORM Reference:** https://scorm.com/scorm-explained/technical-scorm/golf-examples/

**Example Package:** https://scorm.com/wp-content/assets/golf_examples/PIFS/ContentPackagingSingleSCO_SCORM12.zip (downloaded to `/workspace/ilx-demo-ninjasquad/scorm_example/`)

**Stakeholder:** U0A9RDPHQCE (via Slack)

---

## 2. Problem Statement

The Ninja Academy course content currently lives as a web page. Organizations that use LMS platforms (Moodle, Canvas, Blackboard, etc.) need this content delivered as a SCORM 1.2 package so they can:
- Import the course into their LMS
- Track learner progress (completion, scores, bookmarks)
- Report on learner outcomes

---

## 3. Goals & Success Criteria

| Goal | Success Criteria |
|------|-----------------|
| SCORM 1.2 compliance | Package validates against SCORM 1.2 spec; `imsmanifest.xml` is well-formed with correct namespaces |
| Full course content | All 3 modules / 8 lessons are included with their content |
| LMS compatibility | Package can be uploaded to a SCORM 1.2-compliant LMS and launched |
| Learner tracking | SCO communicates with LMS API: lesson_status, score, session_time, bookmarking |
| Professional UX | Clean, readable design with responsive layout and course navigation |
| Quiz/Assessment | Each module includes a quiz; final score is reported to the LMS |

---

## 4. Course Structure

### Source Content: 3 Modules, 8 Lessons (64 minutes total)

**Module 1: Strategic Assessment and Service Mapping**
- Lesson 1.1: Migration Drivers and Business Case Development (8 min)
- Lesson 1.2: Comprehensive GCP-to-AWS Service Mapping (8 min)
- Lesson 1.3: Application Portfolio Analysis and Wave Planning (8 min)

**Module 2: Technical Migration Execution**
- Lesson 2.1: Infrastructure-as-Code Conversion and Environment Provisioning (8 min)
- Lesson 2.2: Data Migration Strategies and Transfer Optimization (8 min)
- Lesson 2.3: Application Cutover and Validation Procedures (8 min)

**Module 3: Optimization and Operational Excellence**
- Lesson 3.1: Cost Optimization and Financial Operations (8 min)
- Lesson 3.2: Performance Tuning and Architectural Optimization (8 min)

---

## 5. SCORM 1.2 Package Architecture

### Package Type: Single SCO with Internal Navigation

Following the golf example's "Content Packaging Single SCO" pattern:

```
scorm_package/
├── imsmanifest.xml              # SCORM manifest (root)
├── adlcp_rootv1p2.xsd           # ADL SCORM 1.2 schema
├── imscp_rootv1p1p2.xsd         # IMS Content Packaging schema
├── imsmd_rootv1p2p1.xsd         # IMS Metadata schema
├── ims_xml.xsd                  # IMS base XML schema
├── shared/
│   ├── launchpage.html           # Entry point — course hub with nav
│   ├── scormfunctions.js         # SCORM 1.2 API wrapper
│   ├── contentfunctions.js       # Shared content helpers
│   ├── navigation.js             # Internal lesson navigation & bookmarking
│   ├── assessment.html           # Quiz/assessment template
│   ├── assessment.js             # Quiz engine
│   └── style.css                 # Global styles
├── module1/
│   ├── lesson1_1.html            # Migration Drivers and Business Case
│   ├── lesson1_2.html            # GCP-to-AWS Service Mapping
│   ├── lesson1_3.html            # Application Portfolio Analysis
│   └── questions.js              # Module 1 quiz questions
├── module2/
│   ├── lesson2_1.html            # IaC Conversion and Provisioning
│   ├── lesson2_2.html            # Data Migration Strategies
│   ├── lesson2_3.html            # Application Cutover and Validation
│   └── questions.js              # Module 2 quiz questions
├── module3/
│   ├── lesson3_1.html            # Cost Optimization and FinOps
│   ├── lesson3_2.html            # Performance Tuning and Optimization
│   └── questions.js              # Module 3 quiz questions
└── assets/
    ├── images/                   # Module infographics, diagrams
    └── icons/                    # Navigation icons
```

### imsmanifest.xml Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="com.ninjasquad.cloud-migration-course.scorm12" version="1"
         xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
         xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="...">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="default_org">
    <organization identifier="default_org">
      <title>Cloud Computing: Multi-Cloud Migration Strategy — GCP to AWS</title>
      <item identifier="item_1" identifierref="resource_1">
        <title>Cloud Computing: Multi-Cloud Migration Strategy</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="resource_1" type="webcontent"
              adlcp:scormtype="sco" href="shared/launchpage.html">
      <!-- All content files listed here -->
    </resource>
  </resources>
</manifest>
```

---

## 6. SCORM Runtime Requirements

The SCO must implement the SCORM 1.2 Runtime API:

| API Call | Purpose |
|----------|---------|
| `LMSInitialize("")` | Called on SCO launch |
| `LMSFinish("")` | Called on SCO exit/unload |
| `LMSGetValue("cmi.core.lesson_status")` | Read current status |
| `LMSSetValue("cmi.core.lesson_status", "completed")` | Set completion |
| `LMSSetValue("cmi.core.score.raw", score)` | Report quiz score (0-100) |
| `LMSSetValue("cmi.core.lesson_location", bookmark)` | Save bookmark |
| `LMSGetValue("cmi.core.lesson_location")` | Restore bookmark |
| `LMSSetValue("cmi.suspend_data", state)` | Save progress state |
| `LMSGetValue("cmi.suspend_data")` | Restore progress state |
| `LMSSetValue("cmi.core.session_time", time)` | Report session time |
| `LMSCommit("")` | Persist data |

### Tracking Logic
- **Lesson status**: Set to `"incomplete"` on first launch, `"completed"` when all lessons viewed and quiz taken
- **Score**: Raw score 0-100 based on quiz performance across all modules
- **Bookmarking**: Save current lesson position so learner can resume
- **Suspend data**: JSON string storing per-lesson completion and quiz answers

---

## 7. Design Requirements

### UX/UI (Pixel)
- Clean, professional design suitable for enterprise LMS embedding
- Course title and module/lesson sidebar navigation
- Current lesson content area with readable typography
- Progress indicator showing lessons completed
- Quiz interface with clear question display and answer selection
- Responsive: must work at 1024px+ (typical LMS content frame width)
- Color scheme: professional blues/grays befitting cloud computing content
- Module infographic images generated for each module header

### Content Pages
- Each lesson rendered as HTML with structured content from the source
- Key data points, tables, and statistics preserved
- Section headings, bullet lists, and numbered lists for readability

---

## 8. Technical Requirements

### Development (Bolt)
- Pure HTML/CSS/JavaScript — no build tools, no frameworks (SCORM packages must be self-contained static files)
- SCORM 1.2 API wrapper in `scormfunctions.js` (find API, initialize, get/set values, finish)
- Navigation system: sidebar TOC + prev/next buttons
- Quiz engine: multiple-choice questions per module, score calculation, report to LMS
- Bookmark/resume: save and restore learner position via `cmi.core.lesson_location` and `cmi.suspend_data`
- Session time tracking: calculate and report `cmi.core.session_time` in `HHHH:MM:SS.SS` format
- Package the final output as a `.zip` file with `imsmanifest.xml` at root
- Include all 4 XSD schema files from the example package
- Reference: use the downloaded example at `/workspace/ilx-demo-ninjasquad/scorm_example/` as a structural guide

### Content Extraction
- Extract full lesson content from the Ninja Academy course API/page
- Preserve all data: statistics, service mappings, frameworks, case studies
- Structure content into clean HTML pages per lesson

### Deployment
- Final deliverable: `scorm_package.zip` at repository root
- The zip must be uploadable to any SCORM 1.2 LMS (Moodle, Canvas, etc.)
- Also serve content locally for testing: `python -m http.server 8080` from the package directory
- Frontend served on port 3000 for browser testing during development

---

## 9. QA Requirements (Scout)

### Testing Checklist
- [ ] `imsmanifest.xml` is valid XML and follows SCORM 1.2 structure
- [ ] ZIP file has `imsmanifest.xml` at root level
- [ ] All files referenced in manifest exist in the package
- [ ] SCO launches successfully (launchpage.html loads)
- [ ] SCORM API wrapper correctly discovers API object
- [ ] All 8 lessons display correct content
- [ ] Navigation (sidebar, prev/next) works across all lessons
- [ ] Quiz questions load and can be answered for each module
- [ ] Score calculation is correct and reported via `LMSSetValue`
- [ ] Bookmark save/restore works (resume mid-course)
- [ ] Session time is tracked and reported
- [ ] Lesson status transitions: not attempted → incomplete → completed
- [ ] No JavaScript errors in browser console
- [ ] Layout is clean at 1024px, 1280px, and 1440px widths
- [ ] All content is readable — no truncation, overflow, or broken layouts

### Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)

### E2E Testing
- Use `browser_interface.py` for automated browser testing
- See [BROWSER_AUTOMATION.md](BROWSER_AUTOMATION.md) for full API reference
- Capture screenshots of each lesson, quiz, and navigation state

---

## 10. Task Breakdown & Agent Assignments

### Phase 1: Design (Pixel)
1. **Design: Course UI/UX mockup** — Create visual design for the SCORM course including layout, navigation, color scheme, typography, and quiz interface
2. **Design: Module infographic images** — Generate header images for each of the 3 modules

### Phase 2: Development (Bolt)
3. **Implement: SCORM 1.2 manifest and package structure** — Create `imsmanifest.xml`, include XSD schemas, set up directory structure
4. **Implement: SCORM API wrapper (scormfunctions.js)** — API discovery, LMSInitialize/Finish, get/set values, error handling
5. **Implement: Course content pages (8 lessons)** — Extract content from source, create HTML pages for all lessons
6. **Implement: Navigation system** — Sidebar TOC, prev/next buttons, progress tracking, bookmark/resume
7. **Implement: Quiz/assessment engine** — Multiple-choice questions per module, scoring, LMS score reporting
8. **Implement: Package and deliver SCORM zip** — Bundle everything into `scorm_package.zip` with manifest at root

### Phase 3: QA (Scout)
9. **Test: SCORM package validation** — Validate manifest, file references, package structure
10. **Test: E2E browser testing** — Launch course, navigate all lessons, complete quizzes, verify SCORM API calls, check responsive layout

---

## 11. Dependencies

```
Pixel (Design) ──→ Bolt (Development) ──→ Scout (QA)
     │                    │
     │ Design mockup      │ Built course
     │ Module images      │ SCORM package
     └────────────────────┘
```

- Bolt depends on Pixel's design mockup for styling/layout reference
- Bolt depends on Pixel's module images for inclusion in the package
- Scout depends on Bolt's completed SCORM package for testing
- Bolt can start on SCORM infrastructure (manifest, API wrapper) in parallel with Pixel's design work

---

## 12. Out of Scope

- SCORM 2004 support (only SCORM 1.2)
- Video content or multimedia beyond images
- Multi-SCO architecture (using single SCO approach)
- LMS server-side integration testing
- Mobile-first responsive design (LMS frames are typically desktop-width)
- User authentication or enrollment

---

## 13. References

- [SCORM 1.2 Golf Example (downloaded)](/workspace/ilx-demo-ninjasquad/scorm_example/)
- [SCORM Explained — Golf Examples](https://scorm.com/scorm-explained/technical-scorm/golf-examples/)
- [Course Source](https://ninja-academy.builtbyninja.com/courses/cloud-computing-multi-cloud-migration-strategy-gcp-to-aws-platform-transition)
- [DEPLOYMENT.md](DEPLOYMENT.md) — Sandbox networking for testing
- [BROWSER_AUTOMATION.md](BROWSER_AUTOMATION.md) — E2E test tooling
- [LITELLM_GUIDE.md](LITELLM_GUIDE.md) — AI model utilities
