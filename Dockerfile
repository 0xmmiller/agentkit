FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
FROM python:3.12-slim
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY src ./src
USER app
EXPOSE 8010
CMD ["uvicorn", "agentkit.main:app", "--host", "0.0.0.0", "--port", "8010"]
