import pandas as pd
import json, sys

def evaluate(pred_df, truth_df):
    """
    Evaluates predictions against ground truth.
    Returns a dict with detailed metrics.
    """
    merged = pd.merge(truth_df, pred_df, on='case_id', suffixes=('_truth', '_pred'))
    total_cases = len(merged)
    
    status_matches = sum(merged['deletion_status_truth'] == merged['deletion_status_pred'])
    status_acc = status_matches / total_cases if total_cases > 0 else 0.0
    
    exact_case_matches = 0
    total_truth_steps = 0
    total_pred_steps = 0
    step_matches = 0
    field_matches = 0
    total_fields = 0
    seq_matches = 0
    
    discrepancies = []
    
    for _, row in merged.iterrows():
        cid = row['case_id']
        t_status = row['deletion_status_truth']
        p_status = row['deletion_status_pred']
        
        t_steps = json.loads(row['steps_json_truth']) if isinstance(row['steps_json_truth'], str) else row['steps_json_truth']
        p_steps = json.loads(row['steps_json_pred']) if isinstance(row['steps_json_pred'], str) else row['steps_json_pred']
        
        total_truth_steps += len(t_steps)
        total_pred_steps += len(p_steps)
        
        # Check step by step
        case_exact = (t_status == p_status) and (len(t_steps) == len(p_steps))
        case_seq_match = True
        
        min_len = min(len(t_steps), len(p_steps))
        for i in range(min_len):
            ts = t_steps[i]
            ps = p_steps[i]
            
            # Step match requires phase, system_id, resource_id, operation, state
            core_match = (
                ts.get('phase') == ps.get('phase') and
                ts.get('system_id') == ps.get('system_id') and
                ts.get('resource_id') == ps.get('resource_id') and
                ts.get('operation') == ps.get('operation') and
                ts.get('state') == ps.get('state')
            )
            ev_match = (ts.get('evidence_id') == ps.get('evidence_id'))
            
            if core_match and ev_match:
                step_matches += 1
            else:
                case_exact = False
                case_seq_match = False
            
            # Field level checks
            fields = ['step_no', 'phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id']
            for f in fields:
                total_fields += 1
                if ts.get(f) == ps.get(f):
                    field_matches += 1
        
        if len(t_steps) != len(p_steps):
            case_exact = False
            case_seq_match = False
            # add difference in steps as missed fields
            diff = abs(len(t_steps) - len(p_steps))
            total_fields += diff * 7
            
        if case_exact:
            exact_case_matches += 1
        if case_seq_match and len(t_steps) == len(p_steps):
            seq_matches += 1
        else:
            discrepancies.append({
                'case_id': cid,
                'status_truth': t_status,
                'status_pred': p_status,
                'truth_step_count': len(t_steps),
                'pred_step_count': len(p_steps),
                'truth_steps': t_steps,
                'pred_steps': p_steps
            })
            
    step_precision = step_matches / total_pred_steps if total_pred_steps > 0 else 1.0
    step_recall = step_matches / total_truth_steps if total_truth_steps > 0 else 1.0
    step_f1 = (2 * step_precision * step_recall / (step_precision + step_recall)) if (step_precision + step_recall) > 0 else 0.0
    field_acc = field_matches / total_fields if total_fields > 0 else 0.0
    
    return {
        'total_cases': total_cases,
        'status_accuracy': status_acc,
        'exact_case_matches': exact_case_matches,
        'exact_case_accuracy': exact_case_matches / total_cases if total_cases > 0 else 0.0,
        'step_matches': step_matches,
        'total_truth_steps': total_truth_steps,
        'total_pred_steps': total_pred_steps,
        'step_precision': step_precision,
        'step_recall': step_recall,
        'step_f1': step_f1,
        'field_accuracy': field_acc,
        'sequence_accuracy': seq_matches / total_cases if total_cases > 0 else 0.0,
        'discrepancies': discrepancies
    }

if __name__ == '__main__':
    truth = pd.read_csv('dataset/sample_output.csv')
    res = evaluate(truth, truth)
    print("Self-test on sample_output.csv:")
    print(f"Status Acc: {res['status_accuracy']:.4f}")
    print(f"Exact Case Acc: {res['exact_case_accuracy']:.4f}")
    print(f"Step F1: {res['step_f1']:.4f}")
    print(f"Field Acc: {res['field_accuracy']:.4f}")
    print(f"Seq Acc: {res['sequence_accuracy']:.4f}")
