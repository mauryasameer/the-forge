# meerax is a library + scaffolding CLI, not a batch pipeline — its dependencies live in
# pyproject.toml alongside the source rather than a separate requirements.txt, so there is no
# requirements-before-source layer to cache the way an app image would.
FROM python:3.12-slim

# git is required at runtime: `meerax new` shells out to `git init` when scaffolding a project.
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash meerax
WORKDIR /home/meerax/app

COPY pyproject.toml VERSION README.md ./
COPY meerax ./meerax
RUN pip install --no-cache-dir .

WORKDIR /workspace
RUN chown -R meerax:meerax /home/meerax
USER meerax

ENTRYPOINT ["meerax"]
CMD ["--help"]
