import bentoml
from src.constants import *
from src.income_classifier_users import IncomeClassifierUsers
from bentoml.io import JSON
from typing import Any, Dict
from typing import Optional
from src.data_mapper import InputMapper, OutputMapper
from data_drift import MonitoringService
import pickle
from dotenv import dotenv_values
import os
from minio import Minio
import json
import pandas as pd
from evidently.ui.remote import RemoteWorkspace
from evidently_reports import data_drift_report

income_clf_runner = bentoml.mlflow.get(
    "random-forest-classifier:latest"
).to_runner()  # A
full_input_spec = JSON(pydantic_model=IncomeClassifierUsers)
svc = bentoml.Service(
    "income_classifier_service",
    runners=[income_clf_runner],
)


def download_file_from_minio(
    minio_host: str,
    access_key: str,
    secret_key: str,
    bucket_name: str,
    object_name: str,
    file_path: str,
):
    client = Minio(
        endpoint=minio_host, access_key=access_key, secret_key=secret_key, secure=False
    )
    client.fget_object(bucket_name, object_name, file_path)


@svc.on_startup
async def initialise(context: bentoml.Context):
    from src.feature_store import DataStore
    from mlflow.tracking import MlflowClient
    import mlflow

    config = dotenv_values(ENV_FILE_NAME)  # C

    os.environ["FEAST_S3_ENDPOINT_URL"] = config["FEAST_S3_ENDPOINT_URL"]
    os.environ["AWS_ENDPOINT_URL"] = config["FEAST_S3_ENDPOINT_URL"]

    mlflow_client = MlflowClient(config["MLFLOW_HOST"])  # D
    mlflow.set_tracking_uri(config["MLFLOW_HOST"])
    for model in mlflow_client.search_model_versions(
        f"name='{config['MLFLOW_MODEL_NAME']}'"
    ):
        if model.current_stage == config["MLFLOW_MODEL_STAGE"]:
            model_run_id = model.run_id
    mlflow.artifacts.download_artifacts(
        f"runs:/{model_run_id}/column_list.pkl", dst_path="column_list"
    )  # E
    with open("column_list/column_list.pkl", "rb") as f:
        col_list = pickle.load(f)
    feature_store = DataStore(
        config["MINIO_HOST"],
        config["MINIO_ACCESS_KEY"],
        config["MINIO_SECRET_KEY"],
        config["FEATURE_REGISTRY_BUCKET_NAME"],
        config["FEATURE_REGSITRY_FILE_NAME"],
        config["FEAST_S3_ENDPOINT_URL"],
        config["FEAST_REDIS_HOST"],
        config["FEAST_REDIS_PASSWORD"],
    )  # F
    context.state["store"] = feature_store.init_feature_store()  # G
    context.state["col_list"] = col_list
    context.state["feature_list"] = [
        "demographic:Sex",
        "demographic:Native_country",
        "demographic:Race",
        "relationship:Relationship",
        "relationship:Marital-Status",  # Make sure there's no extra colon in the actual feature name
        "occupation:Workclass",
        "occupation:Education",
        "occupation:Occupation",
    ]
    run = mlflow.get_run(model_run_id)
    dataset_source = None

    for dataset_input in run.inputs.dataset_inputs:
        for tag in dataset_input.tags:
            if tag.value == config["REFERENCE_DATASET_NAME"]:
                dataset_source = json.loads(dataset_input.dataset.source)["uri"]
                break

    if not dataset_source:
        raise ValueError(
            f"Reference dataset {config['REFERENCE_DATASET_NAME']} not found."
        )

    bucket_name = dataset_source.split("/")[0]
    object_name = "/".join(dataset_source.split("/")[1:])
    file_path = object_name.split("/")[-1]
    print(bucket_name, object_name, file_path)

    download_file_from_minio(
        minio_host=config["MINIO_HOST"],
        access_key=config["MINIO_ACCESS_KEY"],
        secret_key=config["MINIO_SECRET_KEY"],
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=file_path,
    )

    reference_df = pd.read_csv(file_path)

    evidently_workspace = RemoteWorkspace(config["EVIDENTLY_WORKSPACE_URL"])
    context.state["evidently_workspace"] = evidently_workspace
    context.state["monitoring_service"] = MonitoringService(
        report=data_drift_report,
        reference=reference_df,
        workspace=evidently_workspace,
        project_id=config["EVIDENTLY_PROJECT_ID"],
        window_size=config["EVIDENTLY_REPORT_WINDOW_SIZE"],
    )


@svc.api(input=full_input_spec, output=JSON(), route="/predict")
def predict(inputs: IncomeClassifierUsers, ctx: bentoml.Context) -> Dict[str, Any]:
    input_dict = inputs.dict()  # A
    feature_df = (
        ctx.state["store"]
        .get_online_features(
            features=ctx.state["feature_list"], entity_rows=[input_dict]
        )
        .to_df()
    )  # B
    print(feature_df.head())
    feature_df.drop(columns=["user_id"], inplace=True)
    ctx.state["monitoring_service"].iterate(feature_df)
    data_mapper = InputMapper(feature_df, ctx.state["col_list"])
    input_df = data_mapper.generate_pandas_dataframe()  # C
    output_mapper = OutputMapper(income_clf_runner.predict.run(input_df)[0])  # D
    return {
        "income_category": output_mapper.map_prediction(),
        "user_id": input_dict["user_id"],
    }  # E
