FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --frozen

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]