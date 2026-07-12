FROM python:3.13-slim AS development

LABEL maintainer="bmstu-itstech"

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_ROOT_USER_ACTION=ignore \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PROJECT_ENVIRONMENT=/usr/local \
  UV_CACHE_DIR='/var/cache/uv'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
        build-essential \
        libpq-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y  \
    && rm -rf /var/lib/apt/lists/*

# Installing `uv` package manager:
# https://github.com/astral-sh/uv
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

WORKDIR /code

# Copy only requirements, to cache them in docker layer:
COPY ./uv.lock ./pyproject.toml /code/

# Project initialization
RUN --mount=type=cache,target="$UV_CACHE_DIR" uv sync

# Run main.py
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]

FROM development AS production
COPY . /code
