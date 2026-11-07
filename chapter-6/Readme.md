# Design a Machine Learning System (From Scratch) Chapter 6
## Getting Started

### BentoML
Setup a virtual envrionment by running

```
python3.10 -m venv myvenv
source myvenv/bin/activate
```

Install BentoML by running
```
pip install bentoml==1.1.10
```
To Run the BentoML service in local run the following commands
```
cd bentoml
bentoml build -f bento/bentofile.yaml # For service without data drift detection
bentoml build -f bento/bentofile_with_drift_detection.yaml # For service with data drift detection

```
Once Bento is built please containerize it by running
```
bentoml containerize income_classifier_service:<tag_id>
```
Before running the BentoML service locally please run the following port-forward commands
```
kubectl port-forward svc/mlflow-service -n mlflow 5000:5000
kubectl port-forward svc/redis-deployment-master -n redis 6379:6379
kubectl port-forward svc/minio-service 9000:9000 -n kubeflow
kubectl port-forward svc/evidently-service-internal 8000:8000 -n evidently # For data drift detection service
```
Also please validate the environment config in .env and production.env files. They should have the correct values for the environment/configuration variables. Especially Redis/Minio/MLFlow/Feast/Evidently.

Can make the service available on local by running docker run command

```
docker run --rm -p 3000:3000 income_classifier_service:<tag_id>
```
**Before building Bento for Production please change the ENV variable in bentofile.yaml to production**

### Evidently

port forward to evidently service before running the command
```
kubectl port-forward svc/evidently-service-internal 8000:8000 -n evidently
```
Creat a remote project by running the following command
```
cd evidently
python scripts/create_remote_project.py
```
Can build a dashboard in the remote workspace for the incom-classifier project by running the following command
```
cd evidently
python scripts/build_evidently_dashboard.py
```
Once done can setup compile the Kubeflow pipeline by running the following command
```
cd evidently/kubeflow-pipeline
python inference_pipeline.py
```
Can run the pipeline by uploading the pipeline yaml file to Kubeflow pipeline UI. Can you the makefile to build and push docker images. THe command to build and push the docker image for data-drift is
```
make build-detect-drift
make push-detect-drift
```