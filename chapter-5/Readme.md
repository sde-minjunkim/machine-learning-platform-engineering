# Design a Machine Learning System (From Scratch) Chapter 5
## Getting Started

Setup a virtual envrionment by running

```
python3.10 -m venv myvenv
source myvenv/bin/activate
```

Install all the requirements by running
```
pip install -r requirements.txt
```
## Registering Features in Feast  
To register features in Feast please build and push the docker image which will be eventually used to run the Kubernetes Job. The image contains feature and entity definitions.

'''
cd scripts/feast
docker build -t <docker-username>/feast-job:latest .
docker push <docker-username>/feast-job:latest
'''
After which can run the Kubernetes job by running
```
kubectl apply -f scripts/feast/k8s/job.yaml
```
Your job shoulc successfull run and create a registry.db in minio's feature-registry bucket.

## Building and Pushing Docker Images For Pipeline
Please change the image names in each component.yaml to point to your Docker username. (.i.e replace `varunmallya` with your Docker username)  
The project uses a Makefile to simplify building and pushing Docker images. Here are the available commands:

```
# Build all images
make build-all

# Push all images to registry
make push-all

# Build and push individual components
make build-read-minio-data
make push-read-minio-data
make build-retrieve-feast-features
make push-retrieve-feast-features
make build-run-inference
make push-run-inference
make build-write-minio-data
make push-write-minio-data
```

By default, images are pushed to your configured Docker registry. To change the registry:
```
export DOCKER_REGISTRY=your-registry.io
```

## Compiling and Deploying the Pipeline

To compile the inference pipeline:

```
python inference_pipeline.py
```

This will generate a compiled pipeline file (`inference_pipeline.yaml`) that can be used to deploy the pipeline in Kubeflow Pipelines. The instructions to deploy Kubeflow can be found in the appendix.
