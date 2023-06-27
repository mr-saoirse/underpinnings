FROM python:3.10-slim as base

RUN apt update && apt install -y curl gpg
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg;
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null;
RUN apt install -y git gh
RUN pip install -U pip poetry

WORKDIR /app

#FROM base as builder

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root --no-interaction --no-ansi

COPY ./underpin /app/underpin
COPY ./README.md /app/README.md
RUN poetry install


# FROM base as final
#ready
#WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV PYTHONUNBUFFERED=0

ENTRYPOINT [ "poetry", "run", "underpin" ]

#docker tag underpinnings mrsaoirse/underpinnings