from minio import Minio
import pandas as pd
from evidently.ui.base import Project
from evidently.report import Report
from evidently.metrics import ColumnDriftMetric, ColumnSummaryMetric
from evidently.metrics import DatasetDriftMetric, DatasetMissingValuesMetric
from evidently.ui.remote import RemoteWorkspace
import mlflow
from mlflow import MlflowClient
import json
import argparse
import os


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


def create_evidently_project(
    workspace: RemoteWorkspace, evidently_ui_project_name: str
) -> Project:
    return workspace.create_project(
        name=evidently_ui_project_name,
        description="Used to classify users into multiple income bands",
    )


def get_evidently_project(
    workspace: RemoteWorkspace, evidently_ui_project_name: str
) -> Project:
    projects = workspace.search_project(evidently_ui_project_name)
    if len(projects) == 0:
        return create_evidently_project(workspace, evidently_ui_project_name)

    else:
        return projects[0]


def detect_drift(
    model_name: str,
    model_stage: str,
    mlflow_host: str,
    minio_host: str,
    access_key: str,
    secret_key: str,
    reference_dataset_name: str,
    feature_dataset_path: str,
    evidently_workspace_url: str,
    evidently_ui_project_name: str,
):
    os.environ["AWS_ACCESS_KEY_ID"] = access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
    if not minio_host.startswith("http"):
        os.environ["AWS_ENDPOINT_URL"] = "http://" + minio_host
    else:
        os.environ["AWS_ENDPOINT_URL"] = minio_host
    mlflow.set_tracking_uri(mlflow_host)
    mlflow_client = MlflowClient(mlflow_host)
    evidently_workspace = RemoteWorkspace(evidently_workspace_url)

    model_run_id = None
    for model in mlflow_client.search_model_versions(f"name='{model_name}'"):
        if model.current_stage == model_stage:
            model_run_id = model.run_id
            break

    if not model_run_id:
        raise ValueError(f"Model in stage {model_stage} not found for {model_name}.")

    run = mlflow.get_run(model_run_id)
    dataset_source = None

    for dataset_input in run.inputs.dataset_inputs:
        for tag in dataset_input.tags:
            if tag.value == reference_dataset_name:
                dataset_source = json.loads(dataset_input.dataset.source)["uri"]
                break

    if not dataset_source:
        raise ValueError(f"Reference dataset {reference_dataset_name} not found.")

    bucket_name = dataset_source.split("/")[0]
    object_name = "/".join(dataset_source.split("/")[1:])
    file_path = object_name.split("/")[-1]

    download_file_from_minio(
        minio_host=minio_host,
        access_key=access_key,
        secret_key=secret_key,
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=file_path,
    )

    reference_df = pd.read_csv(file_path)
    feature_df = pd.read_parquet(feature_dataset_path)
    feature_df.drop(columns=["user_id"], errors="ignore", inplace=True)

    report = Report(
        metrics=[
            DatasetDriftMetric(),
            DatasetMissingValuesMetric(),
            ColumnDriftMetric(column_name="Education"),
            ColumnSummaryMetric(column_name="Education"),
            ColumnDriftMetric(column_name="Marital-Status"),
            ColumnSummaryMetric(column_name="Marital-Status"),
            ColumnDriftMetric(column_name="Native_country"),
            ColumnSummaryMetric(column_name="Native_country"),
            ColumnDriftMetric(column_name="Occupation"),
            ColumnSummaryMetric(column_name="Occupation"),
            ColumnDriftMetric(column_name="Race"),
            ColumnSummaryMetric(column_name="Race"),
            ColumnDriftMetric(column_name="Relationship"),
            ColumnSummaryMetric(column_name="Relationship"),
            ColumnDriftMetric(column_name="Sex"),
            ColumnSummaryMetric(column_name="Sex"),
            ColumnDriftMetric(column_name="Workclass"),
            ColumnSummaryMetric(column_name="Workclass"),
        ],
    )
    report.run(reference_data=reference_df, current_data=feature_df)

    report_file_path = "drift_report.json"
    with open(report_file_path, "w") as f:
        f.write(report.json())
    print("report written")
    project = get_evidently_project(evidently_workspace, evidently_ui_project_name)
    print("project retreived")
    evidently_workspace.add_report(project.id, report)
    project.save()


def main():
    parser = argparse.ArgumentParser(description="Detect drift in ML models.")
    parser.add_argument(
        "--model_name", type=str, required=True, help="Name of the model."
    )
    parser.add_argument(
        "--model_stage",
        type=str,
        required=True,
        help="Stage of the model (e.g., production).",
    )
    parser.add_argument(
        "--mlflow_host", type=str, required=True, help="MLflow tracking URI."
    )
    parser.add_argument("--minio_host", type=str, required=True, help="MinIO host URL.")
    parser.add_argument(
        "--access_key", type=str, required=True, help="MinIO access key."
    )
    parser.add_argument(
        "--secret_key", type=str, required=True, help="MinIO secret key."
    )
    parser.add_argument(
        "--reference_dataset_name",
        type=str,
        required=True,
        help="Name of the reference dataset.",
    )
    parser.add_argument(
        "--feature_dataset_path",
        type=str,
        required=True,
        help="Path to the feature dataset.",
    )
    parser.add_argument(
        "--evidently_workspace_url",
        type=str,
        required=True,
        help="Evidently workspace URL.",
    )
    parser.add_argument(
        "--evidently_ui_project_name",
        type=str,
        required=True,
        help="Evidently UI project name.",
    )

    args = parser.parse_args()

    detect_drift(
        model_name=args.model_name,
        model_stage=args.model_stage,
        mlflow_host=args.mlflow_host,
        minio_host=args.minio_host,
        access_key=args.access_key,
        secret_key=args.secret_key,
        reference_dataset_name=args.reference_dataset_name,
        feature_dataset_path=args.feature_dataset_path,
        evidently_workspace_url=args.evidently_workspace_url,
        evidently_ui_project_name=args.evidently_ui_project_name,
    )


# Call the main function
if __name__ == "__main__":
    main()
