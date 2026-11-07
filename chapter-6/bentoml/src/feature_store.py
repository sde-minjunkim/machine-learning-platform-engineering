from feast import FeatureStore
import pandas as pd
from pathlib import Path
from minio import Minio
from pathlib import Path
from feast import FeatureStore
from feast.repo_config import FeastConfigError
from pydantic import ValidationError
import os
import yaml


class DataStore:
    def __init__(
        self,
        minio_host,
        access_key,
        secret_key,
        bucket_name,
        file_name,
        boto_endpoint_url,
        feast_redis_host,
        feast_redis_password,
    ):
        self.minio_host = minio_host
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.boto_endpoint_url = boto_endpoint_url
        self.redis_host = feast_redis_host
        self.redis_password = feast_redis_password

    def init_feature_store(self) -> FeatureStore:
        # Download the content of the feature_store.yaml from the GCS bucket
        client = Minio(
            self.minio_host,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        client.fget_object(self.bucket_name, self.file_name, "feature_store.yaml")
        config_path = Path("./") / "feature_store.yaml"
        with open(config_path, "r") as file:
            feast_config = yaml.safe_load(file)
        feast_config["online_store"][
            "connection_string"
        ] = f"{self.redis_host}:6379,password={self.redis_password}"
        with open(config_path, "w") as file:
            yaml.safe_dump(feast_config, file)

        try:
            os.environ["AWS_ACCESS_KEY_ID"] = self.access_key
            os.environ["AWS_SECRET_ACCESS_KEY"] = self.secret_key
            os.environ["FEAST_S3_ENDPOINT_URL"] = self.boto_endpoint_url
            store = FeatureStore(repo_path=".", fs_yaml_file=config_path)
        except ValidationError as e:
            raise FeastConfigError(e, config_path)
        return store
