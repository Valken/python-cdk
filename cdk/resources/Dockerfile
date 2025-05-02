ARG PYTHON_VERSION
ARG IMAGE=public.ecr.aws/sam/build-python${PYTHON_VERSION}
FROM $IMAGE

ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
ARG HTTPS_PROXY
ARG UV_VERSION=0.4.20

ENV PIP_CACHE_DIR=/tmp/pip-cache
ENV UV_CACHE_DIR=/tmp/uv-cache

RUN mkdir /tmp/pip-cache && \
    chmod -R 777 /tmp/pip-cache && \
    pip install uv==$UV_VERSION && \
    rm -rf /tmp/pip-cache/*

CMD [ "python" ]
