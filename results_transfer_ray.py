import os
import json
import re

local_base = '/Users/scoot/A1/simOutput/ray/v45_optuna1'
expanse_base = '/Users/scoot/A1/simOutput/v45_optuna1_expanse'
test_base = '/Users/scoot/A1/simOutput/ray/v45_optuna1_test'

os.makedirs(test_base, exist_ok=True)

def extract_first_json(text):
    stack = []
    start = None
    for i, c in enumerate(text):
        if c == '{':
            if not stack:
                start = i
            stack.append('{')
        elif c == '}':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    return text[start:i+1]
    return None

for run in os.listdir(local_base):
    run_dir = os.path.join(local_base, run)
    if not os.path.isdir(run_dir):
        continue
    result_json = os.path.join(run_dir, 'result.json')
    if not (os.path.exists(result_json) and os.path.getsize(result_json) == 0):
        continue
    m = re.match(r'run_([0-9a-f]{8})_', run)
    if not m:
        print(f'Could not extract id from {run}')
        continue
    run_id = m.group(1)
    out_file = os.path.join(expanse_base, f'v45_optuna1_{run_id}.out')
    if not os.path.exists(out_file):
        print(f'No .out file found for {run} (expected {out_file})')
        continue
    with open(out_file, 'r') as f:
        data = f.read()
    json_str = extract_first_json(data)
    if not json_str:
        print(f'No JSON object found in {out_file}')
        continue
    try:
        result = json.loads(json_str)
    except Exception as e:
        print(f'Failed to parse JSON in {out_file}: {e}')
        continue
    test_run_dir = os.path.join(test_base, run)
    os.makedirs(test_run_dir, exist_ok=True)
    test_result_json = os.path.join(test_run_dir, 'result.json')
    with open(test_result_json, 'w') as f:
        json.dump(result, f, indent=None)  # No indent for single-line JSON
    print(f'Wrote {test_result_json}')
