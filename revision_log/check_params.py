from recursive_diff import recursive_diff
import json
import re
import pandas

pattern0 = re.compile(r"Pair (\w+):(.*) is in (LHS|RHS) only")

pattern1 = re.compile(
    r"\[(.+?)\]: object type differs: (\w+) != (\w+)|"  # For type differences
    r"\[(.+?)\]: ([^ ]+) != ([^ ]+)"                     # For value differences
)

with open('old_params.json', 'r') as fptr:
    lhs = json.load(fptr)['net']['params']

with open('new_params.json', 'r') as fptr:
    rhs = json.load(fptr)['net']['params']

sides = {
    'LHS': [],
    'RHS': [],
}
diffs = []

series_list = []

for diff_str in recursive_diff(lhs, rhs):
    print(diff_str)
    match = pattern0.search(diff_str)
    if match:
        key, value, side = match.groups()
        sides[side].append( (key, value) )
    else:
        match = pattern1.search(diff_str)
        groups = match.groups()
        if match and groups[0] is not None:
            diffs.append((groups[0], groups[1], groups[2]))
        elif match and groups[3] is not None:
            diffs.append((groups[3], groups[4], groups[5]))
        else:
            raise Exception(f"unexpected value found in diff string {diff_str}")

for key, value in sides['LHS']:
    entry = pandas.Series(
        {'attribute': key, 'LHS': value, 'RHS': '<<NONE>>'}
    )
    series_list.append(entry)

for key, value in sides['RHS']:
    entry = pandas.Series(
        {'attribute': key, 'LHS': '<<NONE>>', 'RHS': value}
    )
    series_list.append(entry)

for key, lval, rval in diffs:
    entry = pandas.Series(
        {'attribute': key, 'LHS': lval, 'RHS': rval}
    )
    series_list.append(entry)

df = pandas.DataFrame(series_list)

df.to_csv('diff_params.csv', index=False)