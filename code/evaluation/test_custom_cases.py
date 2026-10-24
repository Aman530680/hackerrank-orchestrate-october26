#!/usr/bin/env python3
"""
Custom Evaluation Test Suite for Ghost Data Still Exists
Northstar Shop Deletion Audit Engine

Defines 3 custom evaluation test cases created by the engineering team:
- Case 1 (custom_case_01): Historical Identity Resolution with Stale Document Attachment (Rule 7 & Rule 14).
  Tests user_07 requesting erasure with primary email; audits whether attachment support_001
  in evidence_58 is flagged as an un-deleted record that must be removed.
- Case 2 (custom_case_02): Multi-system Incomplete Deletion Pipeline (Rule 2, 4, 10).
  Tests user_30 with remaining search index entry, active integration data flow, and unredacted PII.
- Case 3 (custom_case_03): Explicit Non-Deletion Scope / Marketing Opt-Out (Rule 1).
  Tests user requesting marketing email unsubscribe while requesting account retention.
  Must output NOT_APPLICABLE with empty steps_json ([]).
"""

import os
import sys
import json
import pandas as pd

# Add parent path to import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import DeletionAuditEngine
import evaluate_samples

def get_custom_test_suite():
    requests = pd.DataFrame([
        {
            'case_id': 'custom_case_01',
            'email': 'priya.raman@gmail.com',
            'requested_at': '2026-08-20T10:00:00Z',
            'reported_at': '2026-09-01T19:30:00Z',
            'reported_status': 'COMPLETE',
            'audit_at': '2026-09-12T08:00:00Z',
            'request_text': 'I hereby request the complete erasure of all my personal data and account records pursuant to GDPR Article 17.'
        },
        {
            'case_id': 'custom_case_02',
            'email': 'camille.bernard86@outlook.com',
            'requested_at': '2026-08-25T08:00:00Z',
            'reported_at': '2026-08-27T12:00:00Z',
            'reported_status': 'PARTIALLY_COMPLETE',
            'audit_at': '2026-09-15T12:00:00Z',
            'request_text': 'Please delete all my customer data and stop processing my information.'
        },
        {
            'case_id': 'custom_case_03',
            'email': 'customer.service.inquiry@gmail.com',
            'requested_at': '2026-09-10T14:30:00Z',
            'reported_at': '2026-09-11T09:00:00Z',
            'reported_status': 'COMPLETE',
            'audit_at': '2026-09-15T12:00:00Z',
            'request_text': 'Please unsubscribe me from marketing emails only, but keep my account active so I can view my purchase history.'
        }
    ])

    truth = pd.DataFrame([
        {
            'case_id': 'custom_case_01',
            'deletion_status': 'INCOMPLETE',
            'steps_json': json.dumps([
                {
                    'step_no': 1,
                    'phase': 'FINDING',
                    'system_id': 'support_platform',
                    'resource_id': 'support_001',
                    'operation': 'REPORT_REMAINING_RECORD',
                    'state': 'PRESENT',
                    'evidence_id': 'evidence_58'
                },
                {
                    'step_no': 2,
                    'phase': 'REMEDIATION',
                    'system_id': 'support_platform',
                    'resource_id': 'support_001',
                    'operation': 'DELETE_RECORD',
                    'state': 'ABSENT',
                    'evidence_id': ''
                },
                {
                    'step_no': 3,
                    'phase': 'VERIFICATION',
                    'system_id': 'account_service',
                    'resource_id': 'account_007',
                    'operation': 'VERIFY_RECORD_ABSENT',
                    'state': 'ABSENT',
                    'evidence_id': ''
                },
                {
                    'step_no': 4,
                    'phase': 'VERIFICATION',
                    'system_id': 'support_platform',
                    'resource_id': 'support_001',
                    'operation': 'VERIFY_RECORD_ABSENT',
                    'state': 'ABSENT',
                    'evidence_id': ''
                }
            ], separators=(',', ':'))
        },
        {
            'case_id': 'custom_case_02',
            'deletion_status': 'INCOMPLETE',
            'steps_json': json.dumps([
                {
                    'step_no': 1,
                    'phase': 'FINDING',
                    'system_id': 'search_service',
                    'resource_id': 'search_9359',
                    'operation': 'REPORT_REMAINING_RECORD',
                    'state': 'PRESENT',
                    'evidence_id': 'evidence_92'
                },
                {
                    'step_no': 2,
                    'phase': 'FINDING',
                    'system_id': 'analytics_platform',
                    'resource_id': 'analytics_3697',
                    'operation': 'REPORT_EXPOSED_PII',
                    'state': 'PRESENT',
                    'evidence_id': 'evidence_92'
                },
                {
                    'step_no': 3,
                    'phase': 'FINDING',
                    'system_id': 'support_platform',
                    'resource_id': 'support_6477',
                    'operation': 'REPORT_EXPOSED_PII',
                    'state': 'PRESENT',
                    'evidence_id': 'evidence_92'
                },
                {
                    'step_no': 4,
                    'phase': 'FINDING',
                    'system_id': 'integration_service',
                    'resource_id': 'data_flow_8524',
                    'operation': 'REPORT_ACTIVE_DATA_FLOW',
                    'state': 'ACTIVE',
                    'evidence_id': 'evidence_92'
                },
                {
                    'step_no': 5,
                    'phase': 'REMEDIATION',
                    'system_id': 'integration_service',
                    'resource_id': 'data_flow_8524',
                    'operation': 'DISABLE_DATA_FLOW',
                    'state': 'DISABLED',
                    'evidence_id': ''
                },
                {
                    'step_no': 6,
                    'phase': 'REMEDIATION',
                    'system_id': 'search_service',
                    'resource_id': 'search_9359',
                    'operation': 'DELETE_RECORD',
                    'state': 'ABSENT',
                    'evidence_id': ''
                },
                {
                    'step_no': 7,
                    'phase': 'REMEDIATION',
                    'system_id': 'support_platform',
                    'resource_id': 'support_6477',
                    'operation': 'REDACT_RECORD',
                    'state': 'REDACTED',
                    'evidence_id': ''
                },
                {
                    'step_no': 8,
                    'phase': 'REMEDIATION',
                    'system_id': 'analytics_platform',
                    'resource_id': 'analytics_3697',
                    'operation': 'ANONYMIZE_RECORD',
                    'state': 'ANONYMIZED',
                    'evidence_id': ''
                },
                {
                    'step_no': 9,
                    'phase': 'VERIFICATION',
                    'system_id': 'account_service',
                    'resource_id': 'account_4163',
                    'operation': 'VERIFY_RECORD_ABSENT',
                    'state': 'ABSENT',
                    'evidence_id': ''
                },
                {
                    'step_no': 10,
                    'phase': 'VERIFICATION',
                    'system_id': 'search_service',
                    'resource_id': 'search_9359',
                    'operation': 'VERIFY_RECORD_ABSENT',
                    'state': 'ABSENT',
                    'evidence_id': ''
                },
                {
                    'step_no': 11,
                    'phase': 'VERIFICATION',
                    'system_id': 'security_service',
                    'resource_id': 'audit_record_1707',
                    'operation': 'VERIFY_RECORD_PRESENT',
                    'state': 'PRESENT',
                    'evidence_id': ''
                },
                {
                    'step_no': 12,
                    'phase': 'VERIFICATION',
                    'system_id': 'support_platform',
                    'resource_id': 'support_6477',
                    'operation': 'VERIFY_RECORD_REDACTED',
                    'state': 'REDACTED',
                    'evidence_id': ''
                },
                {
                    'step_no': 13,
                    'phase': 'VERIFICATION',
                    'system_id': 'analytics_platform',
                    'resource_id': 'analytics_3697',
                    'operation': 'VERIFY_RECORD_ANONYMIZED',
                    'state': 'ANONYMIZED',
                    'evidence_id': ''
                },
                {
                    'step_no': 14,
                    'phase': 'VERIFICATION',
                    'system_id': 'integration_service',
                    'resource_id': 'data_flow_8524',
                    'operation': 'VERIFY_DATA_FLOW_DISABLED',
                    'state': 'DISABLED',
                    'evidence_id': ''
                }
            ], separators=(',', ':'))
        },
        {
            'case_id': 'custom_case_03',
            'deletion_status': 'NOT_APPLICABLE',
            'steps_json': '[]'
        }
    ])

    return requests, truth

def run_custom_evaluation():
    requests, truth = get_custom_test_suite()
    engine = DeletionAuditEngine(dataset_dir='dataset')
    
    predictions = []
    for _, row in requests.iterrows():
        status, steps_s = engine.audit_case(row)
        predictions.append({
            'case_id': row['case_id'],
            'deletion_status': status,
            'steps_json': steps_s
        })
        
    pred_df = pd.DataFrame(predictions)
    results = evaluate_samples.evaluate(pred_df, truth)
    return results, pred_df, truth

if __name__ == '__main__':
    results, pred_df, truth = run_custom_evaluation()
    print("==================================================")
    print("Custom Evaluation Results:")
    print("==================================================")
    for k, v in results.items():
        if k != 'discrepancies':
            print(f"  {k}: {v}")
