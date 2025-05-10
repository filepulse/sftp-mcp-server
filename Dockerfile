# Stage 1: Build stage
FROM python:3.13-bullseye AS builder

RUN pip install uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

# Create the virtual environment
RUN uv venv .venv

# Install dependencies using global uv (not inside .venv)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Stage 2: Runtime image
FROM python:3.13-bullseye

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

RUN ls

ENTRYPOINT ["python", "server.py"]