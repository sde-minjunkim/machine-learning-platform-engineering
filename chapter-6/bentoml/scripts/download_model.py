import mlflow
import bentoml
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
if not env_path.is_file():
    raise FileNotFoundError(env_path)
load_dotenv(env_path, override=True)

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
model_name = os.environ["MLFLOW_MODEL_NAME"]
model_stage = os.environ["MLFLOW_MODEL_VERSION"]
bentoml.mlflow.import_model(
    model_name, model_uri=f"models:/{model_name}/{model_stage}"
)
