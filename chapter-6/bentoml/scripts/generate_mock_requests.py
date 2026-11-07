import pandas as pd
import requests
import json
import os

mock_request_data = pd.read_csv("mock_request_data.csv")
bentoml_endpoint = os.getenv("BENTO_ENDPOINT")

for index, row in mock_request_data.iterrows():
    request_dict = {"user_id": row["user_id"]}
    requests.post(
        bentoml_endpoint,
        data=json.dumps(request_dict),
    )
