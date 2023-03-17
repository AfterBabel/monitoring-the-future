import pandas as pd
from pathlib import Path
from collections import defaultdict

with open("variable_names.txt") as f:
    variable_names = [line.strip() for line in f]

metadata = pd.read_csv("metadata.tsv", sep="\t")

root = Path('files')

grouped = metadata.groupby(["grade", "form"])
dfs = defaultdict(lambda: defaultdict(list))
for (grade, form), g in grouped:
    for _, row in g.iterrows():
        study_id = row.study.split("_")[1]
        path = root/row.study/row.dataset_name/f"{study_id}-{row.dataset_name[2:]}-Data.dta"
        data_dict = {}
        for col_name, var_name in pd.read_stata(path, iterator=True).variable_labels().items():
            for variable_name in variable_names:
                if var_name and variable_name in var_name:
                    data_dict[col_name] = variable_name

        data_dict["V3"] = "FORM ID"
        data_dict["V1"] = "YEAR"
        data_dict["V5"] = "SAMPLING WEIGHT"
        
        df = pd.read_stata(path, convert_categoricals=False).dropna(axis=1, how="all")
        df.V1 = df.V1.fillna(method="ffill")
        if "V5" not in df.columns:
            df.rename(columns={"ARCHIVE_WT": "V5"}, inplace=True)
        data_dict = {k: data_dict[k] for k in sorted(data_dict.keys(), key=lambda k: int(k[1:]))}
        assert len(df["V1"].unique()) == 1
        assert str(int(df["V1"].iloc[0])) in str(row.year)
        assert len(df["V3"].unique()) == 1
        assert df["V3"].iloc[0] == row.form
        df = df[list(data_dict.keys())] # filter columns
        df.rename(columns=data_dict, inplace=True)
        dfs[grade][form].append(df)

for grade in dfs.keys():
    for form in dfs[grade].keys():
        df = pd.concat(dfs[grade][form])
        df.to_csv(f"grade-{grade}_form-{form}.csv", index=False)