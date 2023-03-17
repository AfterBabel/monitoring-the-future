import re
import pandas as pd
from pathlib import Path
from collections import defaultdict

root = Path('files')
records = []
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
            record = {
                "dataset_name": dataset_name,
                "form": int(form),
                "year": int(year),
                "grade": int(grd),
                "study": study
            }
            records.append(record)
    else:
        grade = re.search(r"(\d+)th-Grade", grade).group(1)
        matches = re.finditer(r"(DS\d{4}) Form (\d+)", manifest)
        for match in matches:
            dataset_name, form = match.groups()
            record = {
                "dataset_name": dataset_name,
                "form": int(form),
                "year": int(year),
                "grade": int(grade),
                "study": study
            }
            records.append(record)

df = pd.DataFrame.from_records(records)
df.to_csv("metadata.tsv", sep="\t", index=False)
            
    