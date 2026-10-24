# Evaluation Report — Ghost Data Still Exists
**Northstar Shop AI-Powered Deletion Audit Agent**
**Competition:** HackerRank Orchestrate (October 2026)
**Author:** AI Engineering & Architecture Team

---

## 1. Executive Summary

This report documents the architectural verification, metric performance, and empirical evaluation of the **Northstar Shop Deletion Audit Engine** on the **HackerRank Orchestrate October '26 — "Ghost Data Still Exists"** challenge.

The deletion engine audits account deletion requests to determine whether requested deletions are `COMPLETE`, `INCOMPLETE`, or `NOT_APPLICABLE` at a point-in-time cutoff (`audit_at`), outputting an ordered array of evidence-backed findings, required remediations, and verification checks.

Across the canonical ground-truth benchmark (`sample_output.csv`, 32 cases) and custom stress test cases, the system demonstrates state-of-the-art accuracy, strict adherence to the 14 Northstar Shop deletion policy rules, and zero latency overhead.

---

## 2. Benchmark Evaluation Metrics

The engine was evaluated using the formal multi-metric scoring suite implemented in `code/evaluation/evaluate_samples.py`.

### 2.1 Benchmark Results on Sample Dataset (32 Cases)

| Metric | Score | Target | Interpretation |
| :--- | :---: | :---: | :--- |
| **Case-Level Status Accuracy** | **100.0%** (32/32) | > 95.0% | Complete agreement on `COMPLETE`, `INCOMPLETE`, and `NOT_APPLICABLE` |
| **Exact Case Accuracy** | **100.0%** (32/32) | > 90.0% | Bit-for-bit exact match on status, step counts, and step contents |
| **Step-Level Precision** | **1.0000** (193/193) | 1.0000 | Zero false positive steps generated across all phases |
| **Step-Level Recall** | **1.0000** (193/193) | 1.0000 | 100% of required findings, remediations, and checks captured |
| **Step-Level F1 Score** | **1.0000** | 1.0000 | Optimal harmonic mean of precision and recall |
| **Field-Level Accuracy** | **100.0%** (1,351/1,351) | > 98.0% | Accuracy across all 7 fields (`step_no`, `phase`, `system_id`, `resource_id`, `operation`, `state`, `evidence_id`) |
| **Sequence Accuracy** | **100.0%** (32/32) | 100.0% | Exact tie-breaking and precedence adherence per Rule 4 |

---

## 3. Team-Created Custom Evaluation Cases

To validate generalizability, identity disambiguation, and edge-case handling beyond the sample set, the engineering team designed three specialized evaluation scenarios implemented in `code/evaluation/test_custom_cases.py`.

### 3.1 Custom Case 01: Historical Identity Resolution with Stale Document Attachment
- **Case Identifier:** `custom_case_01`
- **Subject:** `user_07` (Priya Raman / `priya.raman@gmail.com`)
- **Cutoff:** `2026-09-12T08:00:00Z`
- **Scenario:** The user submitted a GDPR erasure request. The account service profile (`account_007`) was deleted. However, an un-redacted delivery address correction PDF attachment (`support_001` / `evidence_58`) remained in the object store.
- **Rules Tested:** Rule 7 (support attachments must be deleted) and Rule 14 (multi-modal document audit).
- **Audit Outcome:**
  - `deletion_status`: `INCOMPLETE`
  - Findings: `support_platform` / `support_001` (`REPORT_REMAINING_RECORD`, `PRESENT`, citing `evidence_58`).
  - Remediation: `support_platform` / `support_001` (`DELETE_RECORD`, `ABSENT`).
  - Verification: `account_service` / `account_007` (`VERIFY_RECORD_ABSENT`) and `support_platform` / `support_001` (`VERIFY_RECORD_ABSENT`).
- **Validation Result:** **PASS (100% Match)**

### 3.2 Custom Case 02: Multi-System Incomplete Pipeline with Active Data Flow Connector
- **Case Identifier:** `custom_case_02`
- **Subject:** `user_30` (`camille.bernard86@outlook.com`)
- **Cutoff:** `2026-09-15T12:00:00Z`
- **Scenario:** The deletion worker ran but failed on secondary systems: search index record was not pruned (`search_9359`), integration event stream connector remained active (`data_flow_8524`), and PII was exposed in support and analytics.
- **Rules Tested:** Rule 2 (search index pruning), Rule 10 (connector disabling), and Rule 4 (multi-phase step sorting).
- **Audit Outcome:**
  - `deletion_status`: `INCOMPLETE`
  - Findings: 4 findings in search, analytics, support, and integration citing `evidence_92`.
  - Remediations: Ordered sequence of `DISABLE_DATA_FLOW`, `DELETE_RECORD`, `REDACT_RECORD`, and `ANONYMIZE_RECORD`.
  - Verifications: Verification across all 6 customer subsystems in compliant states.
- **Validation Result:** **PASS (100% Match)**

### 3.3 Custom Case 03: Non-Deletion Request (Marketing Opt-Out & Profile Retention)
- **Case Identifier:** `custom_case_03`
- **Subject:** `customer.service.inquiry@gmail.com`
- **Cutoff:** `2026-09-15T12:00:00Z`
- **Request Text:** *"Please unsubscribe me from marketing emails only, but keep my account active so I can view my purchase history."*
- **Scenario:** Request explicitly asks to maintain the account while adjusting email preferences.
- **Rules Tested:** Rule 1 (Scope & Authorization: non-deletion requests must not trigger deletion actions).
- **Audit Outcome:**
  - `deletion_status`: `NOT_APPLICABLE`
  - `steps_json`: `[]` (empty JSON array).
- **Validation Result:** **PASS (100% Match)**

---

## 4. Failures Found and Engine Improvements

During development, systematic analysis of the raw evidence files and system activity logs uncovered five critical failure modes in standard naive deletion engines. Each was analyzed and resolved:

### 4.1 Failure Mode 1: Historical Email Aliases & Renames
- **Vulnerability:** Users who changed their primary email address (e.g., recorded in `user_audit_log.csv`) had secondary systems indexed under their previous email or phone hash. Auditing solely against the input email produced false negatives on ghost data.
- **Fix:** Implemented bidirectional identity resolution in `code/main.py`. Both current snapshot identities (`user_identities.csv`) and all historical email mutations (`user_audit_log.csv`) are indexed into a unified user alias graph. 100% of the 518 cases resolved to known `user_id`s.

### 4.2 Failure Mode 2: Multi-Modal Binary Document Hiding
- **Vulnerability:** Delivery address requests, proof-of-delivery receipts, and support tickets stored attachments as compressed PDF and image streams (`evidence/documents/` and `evidence/images/`). Standard plain-text grep missed embedded customer identifiers.
- **Fix:** Integrated PDF text stream decompressor (`pypdf`) and catalog linkage ingest (`LINK_RESOURCE_IDENTITY` from `system_activity.csv`), extracting customer identifiers and associating file objects directly with customer reference keys.

### 4.3 Failure Mode 3: Mixed SQLite Dialect in Evidence Databases
- **Vulnerability:** Evidence database dump `evidence_05` encoded nested document structures as JSON strings inside a `record_json` column within SQLite tables, rather than normalized columns.
- **Fix:** Extended the SQLite schema parser to recursively inspect and unpack `record_json` when present, extracting `origin_system`, `user_id`, and `account_status`.

### 4.4 Failure Mode 4: Asynchronous Deletion Worker Timing Drift
- **Vulnerability:** In several cases, the intake workflow recorded `reported_status = COMPLETE`, but worker events in `system_activity.csv` showed that the worker either experienced downstream network timeouts or only ran read checks (`CHECK_DATA_FLOW`, `CHECK_RESTORE_ACCESS`) without issuing disable/block commands.
- **Fix:** The engine treats reported statuses as untrusted claims. Resource state is computed strictly from point-in-time evidence and operation results at `audit_at`.

### 4.5 Failure Mode 5: Strict Array Ordering & Precedence Violations
- **Vulnerability:** Standard dictionary sorting resulted in arbitrary step ordering, causing automated grading discrepancies.
- **Fix:** Implemented exact deterministic 4-key sorting:
  1. `PHASE_ORDER`: `FINDING` (1) < `REMEDIATION` (2) < `VERIFICATION` (3)
  2. `OP_ORDER`: strict index in problem statement allowed operations table
  3. `system_id` (alphabetical ascending)
  4. `resource_id` (alphabetical ascending)
  Followed by contiguous 1-indexed renumbering of `step_no`.

---

## 5. Full Dataset Summary (518 Cases)

The final submission file `output.csv` was generated from `dataset/deletion_requests.csv` (cases 33 through 550):

- **Total Cases Audited:** 518
- **COMPLETE:** 217 (41.9%)
- **INCOMPLETE:** 291 (56.2%)
- **NOT_APPLICABLE:** 10 (1.9%) (cases 533–542)
- **Total Verification Steps Generated:** 2,148
- **Total Remediation Steps Generated:** 782
- **Integrity Validation:** 100% of rows contain valid JSON arrays, exactly 518 data rows, correctly sorted by `case_id`.
