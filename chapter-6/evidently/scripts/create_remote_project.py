from evidently.ui.workspace import RemoteWorkspace

ws = RemoteWorkspace("http://localhost:8000")
project = ws.create_project(
    name="income-classifier",
    description="Used to classify users into multiple income bands",
)
