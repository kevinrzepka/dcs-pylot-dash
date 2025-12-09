#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE

# https://hub.docker.com/layers/library/python/3.14.2-slim/images/sha256-c1250d34ec4f97c87c5f95dda74be3f8eeb8d91649e621df7bfbb3dd5f946262
FROM python@sha256:c1250d34ec4f97c87c5f95dda74be3f8eeb8d91649e621df7bfbb3dd5f946262 AS base
ARG UV_VERSION=0.9.16
RUN apt update \
    && apt install -y curl \
    && curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh | sh
# installing to /root/.local/bin -> to add $HOME/.local/bin to your PATH
# both options do not work, uv not found
# RUN . /root/.local/bin/env
# RUN ln -s $HOME/.local/bin/uv uv
RUN apt remove curl -y \
    && apt autoremove -y \
    && apt clean

WORKDIR /app
COPY ./pyproject.toml ./
COPY ./uv.lock ./
RUN $HOME/.local/bin/uv sync --frozen --no-group dev --no-group cyclonedx

FROM python@sha256:c1250d34ec4f97c87c5f95dda74be3f8eeb8d91649e621df7bfbb3dd5f946262 AS runner
WORKDIR /app

# https://linux.die.net/man/8/useradd
RUN useradd -u 1000 -U app
RUN chown 1000:1000 /app && chmod 550 /app

COPY --chown=1000:1000 --chmod=440 --from=base /app/.venv/ .venv/
COPY --chown=1000:1000 --chmod=440 src/ ./
RUN find . -type d -exec chmod 550 {} \;
RUN chmod u+x .venv/bin/python dcs_pylot_dash/main.py

USER 1000

ENV PYTHONPATH=/app
ENTRYPOINT [".venv/bin/python", "dcs_pylot_dash/main.py"]
