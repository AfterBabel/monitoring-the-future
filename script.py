import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

data_dict = defaultdict(list)
root = Path('files')
dfs = []
for fn in root.rglob('ICPSR_*/DS*/*.dta'):
    for col_name, var_name in pd.read_stata(fn, iterator=True).variable_labels().items():
        data_dict[col_name].append(var_name)
    df = pd.read_stata(fn)
    dfs.append(df)

pd.concat(dfs).to_csv("db.csv", index=False)

with open('data_dict.json', 'w') as f:
    json.dump(data_dict, f, indent=4)