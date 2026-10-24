# HackerRank Orchestrate — October 2026
## Ghost Data Still Exists: AI Deletion Audit Engine

**Northstar Shop Production Privacy & Deletion Audit Agent**  
*Autonomous verification of point-in-time compliance under GDPR, CCPA, and Northstar Data Retention Policy.*

---

## 1. Challenge Overview

A customer deletion workflow often reports **Complete** even when sensitive personal data remains scattered across primary databases, replication read-replicas, search indexes, analytics cohorts, customer support attachments, or active integration connectors. Furthermore, automated sync routines and restore procedures can inadvertently bring deleted records back into active production environments.

This engine audits 518 customer account deletion requests at a specific point-in-time cutoff (`audit_at`) to:
1. Verify whether deletion was actually authorized (`COMPLETE`, `INCOMPLETE`, or `NOT_APPLICABLE`).
2. Resolve user identities across historical email changes and identity logs.
3. Discover remaining ghost data, active data flows, and restore risks across 94 multi-modal evidence sources.
4. Output strict, rule-governed remediation and verification plans in `output.csv`.

---

## 2. Architecture & Pipeline

```text
                                  +-----------------------------+
                                  |   Customer Deletion Request |
                                  | (email, requested_at, text) |
                                  +--------------+--------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  | 1. Request Scope Classifier |
                                  |   (Identifies Non-Deletion) |
                                  +--------------+--------------+
                                                 |
                         +-----------------------+-----------------------+
                         | (Authorized Deletion)                         | (Opt-Out / Inquiry)
                         v                                               v
          +-----------------------------+                 +-----------------------------+
          | 2. Identity Resolver        |                 | NOT_APPLICABLE              |
          | (user_identities.csv +      |                 | steps_json = []             |
          |  user_audit_log.csv)        |                 +-----------------------------+
          +--------------+--------------+
                         |
                         v
          +-----------------------------+
          | 3. Multi-Modal Evidence     |
          |    Inspection at audit_at   |
          | (SQL, JSON, TXT, LOG, PDF)  |
          +--------------+--------------+
                         |
                         v
          +-----------------------------+
          | 4. Policy Decision Engine   |
          | (14 Rules in deletion_rules)|
          +--------------+--------------+
                         |
           +-------------+-------------+
           | (Findings Present)        | (All Compliant)
           v                           v
+-----------------------+   +-----------------------+
| INCOMPLETE            |   | COMPLETE              |
| 1. FINDINGS (evidence)|   | 1. VERIFICATION only  |
| 2. REMEDIATION (plan) |   |    (cites evidence)   |
| 3. VERIFICATION (goal)|   +-----------------------+
+-----------------------+
           |                            |
           +-------------+--------------+
                         v
          +-----------------------------+
          | 5. Deterministic Sorter     |
          | Phase -> Op -> Sys -> Res   |
          +--------------+--------------+
                         |
                         v
                    output.csv
```

---

## 3. Setup and Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.12 and 3.13)
- Windows PowerShell, macOS zsh, or Linux bash

### Virtual Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate

# Install required dependencies
pip install pandas numpy pypdf
```

---

## 4. Running the Engine

### Generate Final Submission (`output.csv`)
To run the audit engine over the full 518 cases in `dataset/deletion_requests.csv`:

```bash
python code/main.py
```

This will automatically read the dataset and write the compliant, sorted `output.csv` (518 data rows) directly to the repository root.

### CLI Arguments & Options
```bash
# Run on sample dataset:
python code/main.py --input dataset/sample_deletion_requests.csv --output sample_pred.csv

# Run on custom test file:
python code/main.py --input path/to/my_cases.csv --output path/to/my_output.csv
```

---

## 5. Running Evaluations and Custom Tests

The `code/evaluation/` directory contains complete validation tools and reports:

### 1. Benchmark Evaluation on Sample Ground Truth
```bash
python -c "import sys, os, pandas as pd; sys.path.insert(0, os.path.abspath('code/evaluation')); import evaluate_samples; pred = pd.read_csv('test_sample_out.csv'); truth = pd.read_csv('dataset/sample_output.csv'); print(evaluate_samples.evaluate(pred, truth))"
```
*Current benchmark score:* **100.0% Status Accuracy**, **1.0000 Step F1**, **100.0% Sequence Accuracy**.

### 2. Custom Evaluation Suite (3 Edge Cases)
```bash
python code/evaluation/test_custom_cases.py
```
*Evaluates three custom team-created scenarios:*
1. `custom_case_01`: Historical email mutation with unredacted delivery address PDF attachment.
2. `custom_case_02`: Multi-service incomplete deletion with active integration data flow.
3. `custom_case_03`: Explicit non-deletion marketing opt-out request (`NOT_APPLICABLE`).

---

## 6. Deliverables and Reports

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Submission Output** | `output.csv` (repo root) | Exactly 518 data rows (`case_id,deletion_status,steps_json`), sorted by `case_id`. |
| **Audit Engine Source** | `code/main.py` | Complete runnable audit application and CLI. |
| **Evaluation Report** | `code/evaluation/evaluation_report.md` | Status, step, field, and sequence accuracy, 3 custom cases, failures and fixes. |
| **Token Usage Report** | `code/evaluation/usage_report.md` | Model and token accounting for production and development runs. |
| **Agent Chat Log** | `log.txt` (repo root) | Structured AGENTS.md compliant audit trail. |
| **Archive Package** | `code.zip` (repo root) | Clean distribution archive containing `code/`, `code/evaluation/`, and `README.md`. |

---

## 7. Packaging `code.zip`

To package `code.zip` without bundling large dataset files or virtual environments:

**Windows (PowerShell):**
```powershell
Compress-Archive -Path README.md, code -DestinationPath code.zip -Force
```

**macOS / Linux:**
```bash
zip -r code.zip README.md code -x "*/__pycache__/*" "*/.venv/*" "*/venv/*" "*/node_modules/*" "*/.git/*"
```
