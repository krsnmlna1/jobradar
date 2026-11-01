FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY . .
RUN uv sync --frozen --no-dev --package jobradar

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app/software/api
CMD ["uvicorn", "jobradar.main:app", "--host", "0.0.0.0", "--port", "8000"]
