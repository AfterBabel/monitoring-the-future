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
        if "12th-Grade" not in manifest:
            print(f"{study} does not specify the grade, defaulting to 12th grade")
        grade = "12th-Grade"
        match = re.search(r",\s+(\d{4})\.\s", manifest)
        year = match.group(1)
    if "and" in grade:
        patt1 = r"(DS\d{4}) Monitoring the Future: A Continuing Study of American Youth \(8th-\nand 10th-Grade Surveys\)"
        patt2 = r"(DS\d{4}) Main Data File"
        match1 = re.search(patt1, manifest)
        match2 = re.search(patt2, manifest)
        if match1 or match2:
            if match1:
                matches = re.finditer(patt1, manifest)
            elif match2:
                matches = re.finditer(patt2, manifest)
            else:
                import code; code.interact(local=locals())
            for match in matches:
                dataset_name = match.group(1)
                for g in [8, 10]:
                    dataset_id = len(datasets)
                    dataset = {
                        "dataset_id": dataset_id,
                        "dataset_name": dataset_name,
                        "form": "all",
                        "year": int(year),
                        "grade": g,
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
            patt4 = r"(DS\d{4}) (\d+)th-Grade Form (\d+)"
            patt5 = r"(DS\d{4}) (\d+)th Grade, Form (\d+)"
            if re.search(patt4, manifest):
                matches = list(re.finditer(patt4, manifest))
            elif re.search(patt5, manifest):
                matches = list(re.finditer(patt5, manifest))
            else:
                import code; code.interact(local=locals())
            for match in matches:
                dataset_name, grd, form = match.groups()
                dataset_id = len(datasets)
                dataset = {
                    "dataset_id": dataset_id,
                    "dataset_name": dataset_name,
                    "form": form.strip(),
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
        patt3 = r"(DS\d{4}) Core Data"
        match3 = re.search(patt3, manifest)
        if match3:
            matches = re.finditer(patt3, manifest)
            for match in matches:
                dataset_name = match.group(1)
                dataset_id = len(datasets)
                dataset = {
                    "dataset_id": dataset_id,
                    "dataset_name": dataset_name,
                    "form": "core",
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
        matches = re.finditer(r"(DS\d{4}) Form (\d+)", manifest)
        for match in matches:
            dataset_name, form = match.groups()
            dataset_id = len(datasets)
            dataset = {
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "form": form.strip(),
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
            
    