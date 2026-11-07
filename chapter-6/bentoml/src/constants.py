from pathlib import Path

FEATURE_LIST = [
    "demographic:Sex",
    "demographic:Race",
    "demographic:Native_country",
    "relationship:Relationship",
    "relationship:Marital-Status",
    "occupation:Workclass",
    "occupation:Education",
    "occupation:Occupation",
]

ENV_FILE_NAME = Path(__file__).resolve().parents[3] / ".env"
