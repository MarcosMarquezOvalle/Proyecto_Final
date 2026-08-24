FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi

EXPOSE 8000

CMD ["uvicorn", "proyecto_final.main:app", "--host", "0.0.0.0", "--port", "8000"]
