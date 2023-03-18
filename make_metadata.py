import re
import pandas as pd
from pathlib import Path

root = Path('files')

def get_variables(study, dataset_name):
    study_id = study.split("_")[1]
    path = root/study/dataset_name/f"{study_id}-{dataset_name[2:]}-Data.dta"
    yield from pd.read_stata(path, iterator=True).variable_labels().items()

datasets = []
variables = []
for dir_path in root.rglob('ICPSR_*'):
    study = dir_path.name
    manifest_filepath = next(dir_path.rglob('*-manifest.txt'))
    with open(manifest_filepath) as f:
        manifest = f.read()
    match = re.search(r"\(((?:\d+th\- and )?\d+th\-Grade) Surveys?\), (\d{4})", manifest)
    try:
        assert match is not None
        grade, year = match.groups()
    except AssertionError:
        print(f"{study} does not specify the grade")
        grade = "12th-Grade"
        match = re.search(r",\s+(\d{4})\.\s", manifest)
        year = match.group(1)
    if "and" in grade:
        matches = re.finditer(r"(DS\d{4}) (\d+)th-Grade Form (\d+)", manifest)
        for match in matches:
            dataset_name, grd, form = match.groups()
            dataset_id = len(datasets)
            dataset = {
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "form": int(form),
                "year": int(year),
                "grade": int(grd),
                "study": study
            }
            datasets.append(dataset)
            for col_name, var_name in get_variables(study, dataset_name):
                variable = {
                    "dataset_id": dataset_id,
                    "variable_name": var_name,
                    "column_name": col_name
                }
                variables.append(variable)
    else:
        grade = re.search(r"(\d+)th-Grade", grade).group(1)
        matches = re.finditer(r"(DS\d{4}) Form (\d+)", manifest)
        for match in matches:
            dataset_name, form = match.groups()
            dataset_id = len(datasets)
            dataset = {
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "form": int(form),
                "year": int(year),
                "grade": int(grade),
                "study": study
            }
            datasets.append(dataset)
            for col_name, var_name in get_variables(study, dataset_name):
                variable = {
                    "dataset_id": dataset_id,
                    "variable_name": var_name,
                    "column_name": col_name
                }
                variables.append(variable)


df = pd.DataFrame.from_records(datasets, index="dataset_id")
df.to_csv("datasets.tsv", sep="\t")
df = pd.DataFrame.from_records(variables, index="dataset_id")
mask = df["variable_name"] == ""
df.loc[mask, "variable_name"] = "CASEID"
df.to_csv("variables.tsv", sep="\t")
            
    