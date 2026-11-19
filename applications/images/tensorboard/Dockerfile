FROM python:3.11.15-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN python -m pip install --no-cache-dir tensorboard==2.20.0 \
    && python -m pip check

ENTRYPOINT ["tensorboard"]
