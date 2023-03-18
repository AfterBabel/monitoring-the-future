import pandas as pd
from pathlib import Path
from collections import defaultdict
import re
from Levenshtein import distance

datasets = pd.read_csv("datasets.tsv", sep="\t", index_col="dataset_id")
variables = pd.read_csv("variables.tsv", sep="\t", index_col="dataset_id")
selected_variables = pd.read_csv("selected_variables.tsv", sep="\t", dtype={"irn": str, "form": str})

many_spaces_patt = r"\s{2,}"
alphanum_patt = r"([A-Za-z]+[\d@]+[\w@]*|[\d@]+[A-Za-z]+[\w@]*)"

def get_data_dict(dataset_id):
    mask = variables.index == dataset_id
    vars = {
        "V1": "YEAR",
        "V3": "FORM ID",
        "V5": "SAMPLING WEIGHT"
    }
    remaining_var_names = set([])
    for _, selected_variable in selected_variables.iterrows():
        forms = list(map(lambda form: form.strip(), selected_variable["form"].split(",")))
        if datasets.loc[dataset_id]["form"] not in (forms + ["core", "all"]):
            continue
        v = selected_variable["variable_name"]
        v = v.upper().strip()
        v = re.sub(many_spaces_patt, " ", v)
        candidates = []
        pairs = []
        for _, row in variables[mask].iterrows():
            variable_name = row["variable_name"]
            variable_name = variable_name.upper().strip()
            variable_name = re.sub(many_spaces_patt, " ", variable_name)
            if v in variable_name:
                candidates.append(row["column_name"])
        assert len(candidates) <= 1
        if candidates:
            column_name = candidates[0]
            assert column_name not in vars or v == vars[column_name]
            vars[column_name] = v
        else:
            remaining_var_names.add(v)
    
    unmatched_var_names = set([])
    for v in remaining_var_names:
        pairs = []
        for _, row in variables[mask].iterrows():
            column_name = row["column_name"]
            variable_name = row["variable_name"]
            variable_name = variable_name.upper().strip()
            variable_name = re.sub(many_spaces_patt, " ", variable_name)
            
            if ":" in variable_name:
                splits = variable_name.split(":")
                variable_name = "".join(splits[1:]).strip()
                if v in variable_name:
                    assert column_name not in vars or v == vars[column_name]
                    vars[column_name] = v
                    break
            
            if re.match(alphanum_patt, variable_name):
                variable_name = re.sub(alphanum_patt, "", variable_name).strip()
                if v in variable_name:
                    assert column_name not in vars or v == vars[column_name]
                    vars[column_name] = v
                    break
            
            pairs.append((column_name, variable_name))
        
        column_name, variable_name = sorted(pairs, key=lambda item: distance(item[1], v))[0]
        dist = distance(variable_name, v)
        if column_name in vars or dist > 4:
            unmatched_var_names.add(v)
        else:
            print(f"matching \"{v}\" with \"{variable_name}\" (edit_distance={dist})")
            assert column_name not in vars or v == vars[column_name]
            vars[column_name] = v

    dataset = datasets.loc[dataset_id]
    if unmatched_var_names:
        print(f"unmatched variables: {sorted(list(unmatched_var_names))}", "dataset={dataset_name} form={form} year={year} grade={grade} study={study}".format(**dataset.to_dict()))
    return vars

root = Path('files')

dfs = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
for dataset_id, row in datasets.iterrows():
    study_id = row.study.split("_")[1]
    path = root/row.study/row.dataset_name/f"{study_id}-{row.dataset_name[2:]}-Data.dta"
    data_dict = get_data_dict(dataset_id)
    df = pd.read_stata(path, convert_categoricals=False).dropna(axis=1, how="all")
    df.V1 = df.V1.fillna(method="ffill")
    if "V5" not in df.columns:
        df.rename(columns={"ARCHIVE_WT": "V5"}, inplace=True)
    data_dict = {k: data_dict[k] for k in sorted(data_dict.keys(), key=lambda k: int(k[1:]))}
    assert len(df["V1"].unique()) == 1
    assert str(int(df["V1"].iloc[0])) in str(row.year)
    df.V1 = row.year
    df = df[list(data_dict.keys())] # filter columns
    df.rename(columns=data_dict, inplace=True)
    if row.form == "core" or row.form == "all":
        for form, g in df.groupby("FORM ID"):
            dfs[row.grade][str(form)][row.year].append(g.reset_index(drop=True))
    else:
        dfs[row.grade][str(row.form)][row.year].append(df)

for grade in dfs.keys():
    for form in dfs[grade].keys():
        year_dfs = []
        for year in dfs[grade][form].keys():
            df = pd.concat(dfs[grade][form][year], axis=1)
            df = df.loc[:,~df.columns.duplicated()].copy() # remove duplicated columns
            year_dfs.append(df)
        df = pd.concat(year_dfs, axis=0, ignore_index=True)
        df.to_csv(f"grade-{grade}_form-{form}.csv", index=False)